from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import models
from datetime import timedelta
from decimal import Decimal
from .models import Order, OrderItem
from locations.models import Table, Location
from products.models import Product, Category
from employees.models import Employee
from transactions.models import Transaction
import json
from biznex.utils import send_telegram


def _notify_order_paid(order, total, payment_type, note_prefix="To'landi"):
    """Kassir buyurtmani to'lagach, admin uchun kerakli barcha ma'lumotlarni Telegram guruhga yuboradi."""
    payment_names = {'cash': 'Naqd pul', 'card': 'Karta', 'transfer': "O'tkazma"}
    items = order.orderitem_set.select_related('product').all()
    item_lines = "\n".join(
        f"  • {it.product.name} x{it.quantity:g} = {it.get_subtotal():,.0f} UZS" for it in items
    )
    employee_name = order.employee.name if order.employee else "Belgilanmagan"
    table_name = "Saboy (olib ketish)" if order.is_takeaway else (str(order.table) if order.table else "—")
    text = f"""🧾 <b>Biznex — Buyurtma {note_prefix}</b>
🆔 Buyurtma: #{order.pk}
🪑 Stol: {table_name}
👤 Kassir/Ofitsiant: {employee_name}
💳 To'lov turi: {payment_names.get(payment_type, payment_type)}

🍽 <b>Taomlar:</b>
{item_lines if item_lines else "  Ma'lumot yo'q"}

💰 <b>Jami summa: {total:,.0f} UZS</b>
🕒 {timezone.now().strftime('%d.%m.%Y %H:%M')}"""
    send_telegram(text)


def _auto_expire_kitchen_orders():
    """20 daqiqadan o'tgan buyurtmalarni kitchen viewdan olib tashlash uchun filter"""
    cutoff = timezone.now() - timedelta(minutes=20)
    return cutoff


def _clear_kitchen_if_empty(order):
    """Buyurtmada taom qolmasa, oshpaz panelidan ham, ofitsantning ro'yxatidan ham uchirib yuboramiz"""
    if not order.orderitem_set.exists() and order.sent_to_kitchen:
        order.sent_to_kitchen = False
        order.kitchen_sent_at = None
        order.save(update_fields=['sent_to_kitchen', 'kitchen_sent_at'])


def _deduct_stock(order):
    """Buyurtma to'langanda — sotilgan taomlar miqdorini ombordagi (Product.quantity)
    zaxiradan ayiradi."""
    items = order.orderitem_set.select_related('product').all()
    for item in items:
        Product.objects.filter(pk=item.product_id).update(
            quantity=models.F('quantity') - item.quantity
        )


def _restore_stock(order):
    """Buyurtma bekor qilinganda/o'chirilganda — ayirilgan miqdorni omborga qaytaradi."""
    items = order.orderitem_set.select_related('product').all()
    for item in items:
        Product.objects.filter(pk=item.product_id).update(
            quantity=models.F('quantity') + item.quantity
        )


def order_list(request):
    status = request.GET.get('status', 'open')
    orders = Order.objects.filter(status=status).select_related('table', 'employee') \
        .prefetch_related('orderitem_set').order_by('-created_at')
    status_choices = [("open","Ochiq"),("closed","Yopiq"),("cancelled","Bekor")]
    locations = Location.objects.all()
    context = {
        "orders": orders, "status": status, "active_page": "orders",
        "status_choices": status_choices, "locations": locations,
    }
    return render(request, 'orders/list.html', context)


def order_create(request):
    """Kassir 'Yangi buyurtma' bossa — avtomatik saboy buyurtma yaratiladi.
    (Ofitsant esa o'z panelidan stol tanlab alohida yaratadi — waiter_pos orqali.)"""
    order = Order.objects.create(is_takeaway=True)
    return redirect('orders:pos_takeaway', pk=order.pk)


def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.orderitem_set.select_related('product').all()
    return render(request, 'orders/detail.html', {'order': order, 'items': items, 'active_page': 'orders'})


def pos_view(request, table_id):
    table = get_object_or_404(Table, pk=table_id)
    order = Order.objects.filter(table=table, status='open').first()
    if not order:
        emp = Employee.objects.filter(is_active=True).first()
        order = Order.objects.create(table=table, employee=emp)
        table.status = 'busy'
        table.save()
    elif order.is_paid:
        # Buyurtma allaqachon to'langan — chekni avtomatik ochib, brauzerning chop etish
        # oynasini chiqarib yubormaslik uchun buyurtma tafsilotlariga yo'naltiramiz.
        # Chek kerak bo'lsa, u yerdagi "Chekni qayta chiqarish" tugmasi (silentPrintReceipt)
        # printerga to'g'ridan-to'g'ri, hech qanday oyna ochmasdan yuboradi.
        return redirect('orders:detail', pk=order.pk)

    categories = Category.objects.all()
    cat_id = request.GET.get('cat')
    if cat_id:
        products = Product.objects.filter(category_id=cat_id, is_active=True).order_by('order', 'id')
    else:
        products = Product.objects.filter(is_active=True).order_by('order', 'id')

    from settings_app.models import ReceiptSettings
    pos_columns = ReceiptSettings.get_solo().pos_grid_columns
    products_total_count = Product.objects.filter(is_active=True).count()

    items = order.orderitem_set.select_related('product').all()
    context = {
        'table': table, 'order': order, 'categories': categories,
        'products': products, 'items': items, 'selected_cat': cat_id,
        'active_page': 'orders', 'pos_columns': pos_columns,
        'products_total_count': products_total_count,
    }
    return render(request, 'orders/pos.html', context)


def pos_takeaway(request, pk):
    """Saboy (mijoz o'zi keldi) buyurtma uchun POS — stolsiz"""
    order = get_object_or_404(Order, pk=pk, is_takeaway=True)
    if order.is_paid:
        # Xuddi pos_view'dagi kabi — to'g'ridan-to'g'ri chekka emas, tafsilotlarga yo'naltiramiz,
        # aks holda avtomatik chop etish brauzer oynasini chiqarib yuboradi.
        return redirect('orders:detail', pk=order.pk)

    categories = Category.objects.all()
    cat_id = request.GET.get('cat')
    if cat_id:
        products = Product.objects.filter(category_id=cat_id, is_active=True).order_by('order', 'id')
    else:
        products = Product.objects.filter(is_active=True).order_by('order', 'id')

    from settings_app.models import ReceiptSettings
    pos_columns = ReceiptSettings.get_solo().pos_grid_columns
    products_total_count = Product.objects.filter(is_active=True).count()

    items = order.orderitem_set.select_related('product').all()
    context = {
        'table': None, 'order': order, 'categories': categories,
        'products': products, 'items': items, 'selected_cat': cat_id,
        'active_page': 'orders', 'is_takeaway_mode': True, 'pos_columns': pos_columns,
        'products_total_count': products_total_count,
    }
    return render(request, 'orders/pos.html', context)


def waiter_pos(request):
    table_id = request.GET.get('table_id')
    waiter_id = request.GET.get('waiter_id') or request.session.get('waiter_id')

    table = get_object_or_404(Table, pk=table_id)
    waiter = get_object_or_404(Employee, pk=waiter_id)

    order = Order.objects.filter(table=table, status='open').first()
    if not order:
        order = Order.objects.create(table=table, employee=waiter)
        table.status = 'busy'
        table.save()
    elif not order.employee:
        order.employee = waiter
        order.save()

    categories = Category.objects.all()
    cat_id = request.GET.get('cat')
    if cat_id:
        products = Product.objects.filter(category_id=cat_id, is_active=True).order_by('order', 'id')
    else:
        products = Product.objects.filter(is_active=True).order_by('order', 'id')

    from settings_app.models import ReceiptSettings
    pos_columns = ReceiptSettings.get_solo().pos_grid_columns

    items = order.orderitem_set.select_related('product').all()
    context = {
        'table': table, 'order': order, 'categories': categories,
        'products': products, 'items': items, 'selected_cat': cat_id,
        'waiter': waiter, 'is_waiter_mode': True, 'pos_columns': pos_columns,
    }
    return render(request, 'orders/waiter_pos.html', context)


@require_POST
def add_item(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status != 'open':
        return JsonResponse({'success': False, 'error': "Buyurtma yopilgan, taom qo'shib bo'lmaydi"}, status=400)
    data = json.loads(request.body)
    product = get_object_or_404(Product, pk=data['product_id'])
    qty = Decimal(str(data.get('quantity', 1)))

    item, created = OrderItem.objects.get_or_create(
        order=order, product=product,
        defaults={'price': product.price, 'quantity': qty}
    )
    if not created:
        item.quantity += qty
        item.save()

    return JsonResponse({'success': True, 'total': float(order.get_total()), 'item_count': order.orderitem_set.count()})


@require_POST
def update_item_qty(request, pk):
    """Mahsulot miqdorini o'zgartirish (+/-)"""
    order = get_object_or_404(Order, pk=pk)
    if order.status != 'open':
        return JsonResponse({'success': False, 'error': "Buyurtma yopilgan"}, status=400)
    data = json.loads(request.body)
    product_id = data.get('product_id')
    delta = Decimal(str(data.get('delta', 0)))
    try:
        item = OrderItem.objects.get(order=order, product_id=product_id)
        new_qty = item.quantity + delta
        if new_qty <= 0:
            item.delete()
        else:
            item.quantity = new_qty
            item.save()
    except OrderItem.DoesNotExist:
        if delta > 0:
            product = get_object_or_404(Product, pk=product_id)
            OrderItem.objects.create(order=order, product=product, price=product.price, quantity=delta)

    _clear_kitchen_if_empty(order)

    return JsonResponse({'success': True, 'total': float(order.get_total())})


@require_POST
def remove_item(request, pk):
    """Mijoz taomdan voz kechdi — taom darhol o'chadi va oshpaz panelidan uchib ketadi"""
    order = get_object_or_404(Order, pk=pk)
    if order.status != 'open':
        return JsonResponse({'success': False, 'error': "Buyurtma yopilgan"}, status=400)
    data = json.loads(request.body)
    product_id = data.get('product_id')
    try:
        item = OrderItem.objects.get(order=order, product_id=product_id)
        item.delete()
    except OrderItem.DoesNotExist:
        pass

    _clear_kitchen_if_empty(order)

    return JsonResponse({'success': True, 'total': float(order.get_total())})


@require_POST
def close_order(request, pk):
    """Kassir to'ladi tugmasini bosadi — balansga tushadi"""
    order = get_object_or_404(Order, pk=pk)
    if order.status == 'closed':
        # Allaqachon yopilgan — qayta balansga qo'shilmasin
        return redirect('orders:receipt', pk=order.pk)
    payment_type = request.POST.get('payment_type', 'cash')
    order.status = 'closed'
    order.payment_type = payment_type
    order.is_paid = True
    order.save()
    if order.table:
        order.table.status = 'free'
        order.table.save()

    _deduct_stock(order)

    total = order.get_total()

    # Asosiy balansga qo'shish
    from warehouse.models import Balance
    Balance.add(total)

    Transaction.objects.create(
        order=order, employee=order.employee,
        amount=total, category='order', payment_type=payment_type,
        note=f"Buyurtma #{order.pk} to'landi"
    )
    _notify_order_paid(order, total, payment_type, note_prefix="to'landi")
    return redirect('orders:receipt', pk=order.pk)


@require_POST
def mark_paid(request, pk):
    """Buyurtmalar ro'yhatida kassir To'ladi tugmasi — to'lagandan keyin chek chiqadi"""
    order = get_object_or_404(Order, pk=pk)
    if order.status == 'open' and not order.is_paid:
        payment_type = request.POST.get('payment_type', 'cash')
        order.status = 'closed'
        order.payment_type = payment_type
        order.is_paid = True
        order.save()
        if order.table:
            order.table.status = 'free'
            order.table.save()
        _deduct_stock(order)
        total = order.get_total()
        from warehouse.models import Balance
        Balance.add(total)
        Transaction.objects.create(
            order=order, employee=order.employee,
            amount=total, category='order', payment_type=payment_type,
            note=f"Buyurtma #{order.pk} kassir to'ladi"
        )
        _notify_order_paid(order, total, payment_type, note_prefix="kassir to'ladi")
    if request.POST.get('waiter_mode'):
        return redirect('orders:receipt', pk=order.pk)
    return redirect('orders:receipt', pk=order.pk)


@require_POST
def closed_update_qty(request, pk):
    """Yopilgan (to'langan) buyurtmadagi taom miqdorini kassir/admin tahrirlaydi —
    masalan, oshxonada taom tugab qolib mijozga berilmagan bo'lsa.
    Farq balansga va bog'liq tranzaksiyaga qayta hisoblanadi (tranzaksiya o'chirilmaydi, faqat summasi to'g'rilanadi)."""
    order = get_object_or_404(Order, pk=pk)
    if order.status != 'closed':
        return JsonResponse({'success': False, 'error': "Faqat yopilgan buyurtmalarni shu yerdan tahrirlash mumkin"}, status=400)

    data = json.loads(request.body)
    product_id = data.get('product_id')
    delta = Decimal(str(data.get('delta', 0)))

    old_total = order.get_total()

    try:
        item = OrderItem.objects.get(order=order, product_id=product_id)
        old_qty = item.quantity
        new_qty = item.quantity + delta
        if new_qty <= 0:
            item.delete()
            final_qty = Decimal('0')
        else:
            item.quantity = new_qty
            item.save()
            final_qty = new_qty
    except OrderItem.DoesNotExist:
        old_qty = Decimal('0')
        final_qty = Decimal('0')
        if delta > 0:
            product = get_object_or_404(Product, pk=product_id)
            OrderItem.objects.create(order=order, product=product, price=product.price, quantity=delta)
            final_qty = delta

    # Ombordagi zaxirani sotilgan miqdordagi haqiqiy o'zgarishga moslashtiramiz
    stock_change = final_qty - old_qty  # musbat = ko'proq sotildi (zaxiradan ayiriladi)
    if stock_change != 0:
        Product.objects.filter(pk=product_id).update(quantity=models.F('quantity') - stock_change)

    new_total = order.get_total()
    diff = new_total - old_total

    if diff != 0:
        from warehouse.models import Balance
        Balance.add(diff)
        tx = Transaction.objects.filter(order=order, category='order').first()
        if tx:
            tx.amount = new_total
            tx.note = (tx.note or '') + " (tahrirlangan)"
            tx.save(update_fields=['amount', 'note'])

    return JsonResponse({'success': True, 'total': float(new_total)})


@require_POST
def delete_order(request, pk):
    """Yopilgan buyurtmani butunlay o'chirish — masalan, oshxonada taom tugab qolib,
    mijozga umuman berilmagan bo'lsa. Buyurtma barcha ro'yxatlardan (buyurtmalar, hisobotlar)
    yo'qoladi, summasi balansdan ayiriladi. Lekin bog'liq tranzaksiya o'chirilmaydi — faqat
    "bekor qilingan" deb belgilanadi, shunday qilib Tranzaksiyalar tarixida iz qoladi."""
    order = get_object_or_404(Order, pk=pk)
    if order.status not in ('closed',):
        return JsonResponse({'success': False, 'error': "Faqat yopilgan buyurtmalarni o'chirish mumkin"}, status=400)

    total = order.get_total()
    order.status = 'deleted'
    order.deleted_at = timezone.now()
    order.save(update_fields=['status', 'deleted_at'])

    _restore_stock(order)

    from warehouse.models import Balance
    Balance.subtract(total)

    Transaction.objects.filter(order=order).update(is_voided=True)

    return JsonResponse({'success': True})


def receipt_view(request, pk):
    """To'langan buyurtma uchun chek (chop etish uchun)"""
    from settings_app.models import ReceiptSettings
    order = get_object_or_404(Order, pk=pk)
    items = order.orderitem_set.select_related('product').all()
    settings_obj = ReceiptSettings.get_solo()
    silent = request.GET.get('silent') == '1'
    return render(request, 'orders/receipt.html', {
        'order': order, 'items': items,
        'width_mm': settings_obj.get_width_mm(),
        'font_size_px': settings_obj.font_size_px,
        'auto_print': settings_obj.auto_print,
        'show_logo': settings_obj.show_logo,
        'footer_text': settings_obj.footer_text,
        'silent': silent,
    })


def receipt_preview(request):
    """Sozlamalar sahifasidan 'Namunaviy chek' — chop etishsiz, faqat ko'rinish uchun"""
    from settings_app.models import ReceiptSettings
    from decimal import Decimal

    class FakeProduct:
        def __init__(self, name, unit):
            self.name = name
            self.unit = unit

    class FakeItem:
        def __init__(self, name, unit, price, qty):
            self.product = FakeProduct(name, unit)
            self.price = Decimal(price)
            self.quantity = Decimal(qty)

        def get_subtotal(self):
            return self.price * self.quantity

    class FakeOrder:
        pk = "DEMO"
        table = None
        employee = None
        payment_type = 'cash'
        from django.utils import timezone as _tz
        updated_at = _tz.now()

        def get_total(self):
            return sum(i.get_subtotal() for i in fake_items)

    fake_items = [
        FakeItem("Somsa", "dona", 5000, 1),
        FakeItem("Patir", "dona", 2000, 1),
        FakeItem("Lula kabob", "dona", 32000, 1),
    ]

    settings_obj = ReceiptSettings.get_solo()
    return render(request, 'orders/receipt.html', {
        'order': FakeOrder(), 'items': fake_items,
        'width_mm': settings_obj.get_width_mm(),
        'font_size_px': settings_obj.font_size_px,
        'auto_print': False,
        'show_logo': settings_obj.show_logo,
        'footer_text': settings_obj.footer_text,
    })


@require_POST
def waiter_send_to_kitchen(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.sent_to_kitchen = True
    order.kitchen_sent_at = timezone.now()
    order.save()
    return JsonResponse({'success': True})


@require_POST
def kitchen_mark_ready(request, pk):
    """Oshpaz 'Tayyor' tugmasini bosadi — buyurtma uchib ketadi"""
    order = get_object_or_404(Order, pk=pk)
    order.sent_to_kitchen = False
    order.kitchen_sent_at = None
    order.save()
    return JsonResponse({'success': True})


def kitchen_view(request):
    """Oshpaz ko'rishi — 20 daqiqadan o'tmagan buyurtmalar"""
    cutoff = timezone.now() - timedelta(minutes=20)
    # Auto-expire: 20 daqiqadan o'tgan sent_to_kitchen larni false qilish
    Order.objects.filter(
        sent_to_kitchen=True,
        kitchen_sent_at__lt=cutoff
    ).update(sent_to_kitchen=False, kitchen_sent_at=None)

    orders = Order.objects.filter(
        status='open',
        sent_to_kitchen=True,
    ).select_related('table', 'employee').prefetch_related('orderitem_set__product').order_by('kitchen_sent_at')

    return render(request, 'orders/kitchen.html', {'orders': orders})


def send_daily_report(request):
    from datetime import date as date_cls
    from django.db.models import Sum
    today = timezone.now().date()
    orders_today = Order.objects.filter(status='closed', created_at__date=today)
    total = sum(o.get_total() for o in orders_today)
    count = orders_today.count()

    employees = Employee.objects.filter(is_active=True)
    emp_lines = []
    for e in employees:
        closed = Order.objects.filter(employee=e, status='closed', created_at__date=today)
        emp_total = sum(o.get_total() for o in closed)
        commission = emp_total * e.commission_percent / 100
        if emp_total > 0:
            emp_lines.append(f"  👤 {e.name}: {emp_total:,.0f} UZS savdo, {commission:,.0f} UZS komissiya")

    text = f"""📊 <b>Biznex — Kunlik Hisobot</b>
📅 Sana: {today.strftime('%d.%m.%Y')}

🧾 Jami buyurtmalar: <b>{count} ta</b>
💰 Jami tushum: <b>{total:,.0f} UZS</b>

👥 <b>Xodimlar bo'yicha:</b>
{"".join(chr(10) + l for l in emp_lines) if emp_lines else "  Ma'lumot yo'q"}

✅ Biznex POS tizimi orqali yuborildi"""

    send_telegram(text)
    return JsonResponse({'success': True, 'message': "Telegram guruhga yuborildi"})
