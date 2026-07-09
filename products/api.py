"""
JSON API endpoints — Vue SPA (static/spa/) uchun.
"""
import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from .models import Product, Category
from biznex.utils import safe_decimal


def _product_to_dict(p):
    return {
        'id': p.pk,
        'name': p.name,
        'category_id': p.category_id,
        'category_name': p.category.name if p.category_id else None,
        'price': float(p.price),
        'cost_price': float(p.cost_price),
        'quantity': float(p.quantity),
        'unit': p.unit,
        'is_active': p.is_active,
        'order': p.order,
        'profit_per_unit': float(p.profit_per_unit),
        'profit_margin_percent': float(p.profit_margin_percent),
    }


def _category_to_dict(c):
    return {'id': c.pk, 'name': c.name, 'code': c.code, 'product_count': c.product_count}


def product_list_api(request):
    cat_id = request.GET.get('cat')
    q = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True).select_related('category').order_by('order', 'id')
    if cat_id:
        products = products.filter(category_id=cat_id)
    if q:
        products = products.filter(name__icontains=q)
    return JsonResponse({'results': [_product_to_dict(p) for p in products]})


def category_list_api(request):
    return JsonResponse({'results': [_category_to_dict(c) for c in Category.objects.all()]})


@require_POST
def product_create_api(request):
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': "Noto'g'ri so'rov"}, status=400)
    p = Product.objects.create(
        name=(data.get('name') or '').strip() or 'Nomsiz taom',
        category_id=data.get('category_id') or None,
        price=safe_decimal(data.get('price')),
        cost_price=safe_decimal(data.get('cost_price')),
        quantity=safe_decimal(data.get('quantity')),
        unit=data.get('unit', 'dona'),
    )
    return JsonResponse({'success': True, 'product': _product_to_dict(p)})


@require_POST
def product_edit_api(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': "Noto'g'ri so'rov"}, status=400)
    product.name = (data.get('name') or '').strip() or product.name
    product.category_id = data.get('category_id') or None
    product.price = safe_decimal(data.get('price'))
    product.cost_price = safe_decimal(data.get('cost_price'))
    product.quantity = safe_decimal(data.get('quantity'))
    product.unit = data.get('unit', product.unit)
    product.save()
    return JsonResponse({'success': True, 'product': _product_to_dict(product)})


@require_POST
def product_delete_api(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = False
    product.save()
    return JsonResponse({'success': True})


@require_POST
def product_reorder_api(request):
    """products/views.py:product_reorder bilan bir xil logika."""
    try:
        data = json.loads(request.body)
        ordered_ids = [int(i) for i in data.get('order', [])]
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'error': "Noto'g'ri so'rov"}, status=400)

    if not ordered_ids:
        return JsonResponse({'success': True})

    products = list(Product.objects.filter(pk__in=ordered_ids))
    products_by_id = {p.pk: p for p in products}
    existing_orders = [p.order for p in products]
    base = min(existing_orders) if existing_orders else 0

    for idx, pid in enumerate(ordered_ids):
        p = products_by_id.get(pid)
        if p:
            p.order = base + idx
            p.save(update_fields=['order'])

    return JsonResponse({'success': True})


@require_POST
def category_create_api(request):
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': "Noto'g'ri so'rov"}, status=400)
    c = Category.objects.create(
        name=(data.get('name') or '').strip() or 'Nomsiz kategoriya',
        code=data.get('code', ''),
    )
    return JsonResponse({'success': True, 'category': _category_to_dict(c)})


@require_POST
def category_edit_api(request, pk):
    category = get_object_or_404(Category, pk=pk)
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': "Noto'g'ri so'rov"}, status=400)
    category.name = (data.get('name') or '').strip() or category.name
    category.code = data.get('code', category.code)
    category.save()
    return JsonResponse({'success': True, 'category': _category_to_dict(category)})


@require_POST
def category_delete_api(request, pk):
    category = get_object_or_404(Category, pk=pk)
    product_count = Product.objects.filter(category=category).count()
    if product_count > 0:
        return JsonResponse({
            'success': False,
            'error': f"\"{category.name}\" kategoriyasini o'chirib bo'lmaydi — unda {product_count} ta taom bor.",
        }, status=400)
    category.delete()
    return JsonResponse({'success': True})
