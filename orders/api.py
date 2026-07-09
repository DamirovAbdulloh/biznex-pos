"""
JSON API endpoints — Vue SPA (static/spa/) uchun.
Eski HTML view'lardagi biznes logikani qayta ishlatadi (orders/views.py),
shunda ikki joyda bir xil kod takrorlanmaydi.
"""
import json
from decimal import Decimal

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Order, OrderItem
from products.models import Product
from transactions.models import Transaction
from . import views as order_views  # _deduct_stock, _restore_stock, _notify_order_paid


def _order_to_dict(order, with_items=True):
    data = {
        'id': order.pk,
        'status': order.status,
        'status_display': order.get_status_display(),
        'payment_type': order.payment_type,
        'is_paid': order.is_paid,
        'is_takeaway': order.is_takeaway,
        'sent_to_kitchen': order.sent_to_kitchen,
        'note': order.note,
        'table': {'id': order.table_id, 'name': str(order.table)} if order.table_id else None,
        'employee': {'id': order.employee_id, 'name': order.employee.name} if order.employee_id else None,
        'created_at': order.created_at.isoformat(),
        'updated_at': order.updated_at.isoformat(),
        'total': float(order.get_total()),
    }
    if with_items:
        data['items'] = [
            {
                'id': it.pk,
                'product_id': it.product_id,
                'product_name': it.product.name,
                'quantity': float(it.quantity),
                'price': float(it.price),
                'subtotal': float(it.get_subtotal()),
                'unit': it.product.unit,
            }
            for it in order.orderitem_set.select_related('product').all()
        ]
    return data


def order_list_api(request):
    status = request.GET.get('status', 'open')
    orders = Order.objects.filter(status=status).select_related('table', 'employee') \
        .prefetch_related('orderitem_set__product').order_by('-created_at')
    return JsonResponse({
        'results': [_order_to_dict(o, with_items=True) for o in orders],
        'status': status,
    })


def order_detail_api(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return JsonResponse(_order_to_dict(order))


@require_POST
def order_mark_paid_api(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status == 'open' and not order.is_paid:
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            payload = {}
        payment_type = payload.get('payment_type', 'cash')
        order.status = 'closed'
        order.payment_type = payment_type
        order.is_paid = True
        order.save()
        if order.table:
            order.table.status = 'free'
            order.table.save()
        order_views._deduct_stock(order)
        total = order.get_total()
        from warehouse.models import Balance
        Balance.add(total)
        Transaction.objects.create(
            order=order, employee=order.employee,
            amount=total, category='order', payment_type=payment_type,
            note=f"Buyurtma #{order.pk} kassir to'ladi"
        )
        order_views._notify_order_paid(order, total, payment_type, note_prefix="kassir to'ladi")
    return JsonResponse({'success': True, 'order': _order_to_dict(order)})


@require_POST
def order_delete_api(request, pk):
    """orders/views.py:delete_order bilan bir xil — faqat closed buyurtmalar uchun."""
    order = get_object_or_404(Order, pk=pk)
    if order.status not in ('closed',):
        return JsonResponse({'success': False, 'error': "Faqat yopilgan buyurtmalarni o'chirish mumkin"}, status=400)

    total = order.get_total()
    order.status = 'deleted'
    order.deleted_at = timezone.now()
    order.save(update_fields=['status', 'deleted_at'])

    order_views._restore_stock(order)

    from warehouse.models import Balance
    Balance.subtract(total)
    Transaction.objects.filter(order=order).update(is_voided=True)

    return JsonResponse({'success': True})
