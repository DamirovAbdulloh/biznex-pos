from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from .models import Transaction
from employees.models import Employee
from biznex.utils import safe_decimal, send_telegram

def _parse_date(value, default):
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return default


def transaction_list(request):
    """Tranzaksiyalar ro'yxati — sanadan sanagacha (range) filtri bilan.
    Parametr berilmasa, standart holatda faqat bugungi kun ko'rsatiladi —
    shu tufayli har kuni soat 00:00 dan boshlab kirim/chiqim ro'yxati
    avtomatik ravishda "0" dan boshlanadi (bu kunning tranzaksiyalari yo'q bo'ladi)."""
    today = timezone.now().date()

    # Eski `?date=` parametri bilan orqaga moslik (bitta kunni tanlash uchun)
    legacy_date = request.GET.get('date', '')
    date_from_str = request.GET.get('date_from', '')
    date_to_str = request.GET.get('date_to', '')

    if legacy_date and not date_from_str and not date_to_str:
        date_from_str = date_to_str = legacy_date

    date_from = _parse_date(date_from_str, today)
    date_to = _parse_date(date_to_str, today)
    if date_from > date_to:
        date_from, date_to = date_to, date_from

    # Kirim/chiqim filtri: ?type=in (faqat kirimlar), ?type=out (faqat chiqimlar), bo'sh — hammasi
    tx_type = request.GET.get('type', '')

    transactions = Transaction.objects.filter(
        created_at__date__gte=date_from, created_at__date__lte=date_to
    ).select_related('employee', 'order').order_by('-created_at')
    active = transactions.exclude(is_voided=True)
    total_in = active.filter(amount__gt=0).aggregate(s=Sum('amount'))['s'] or 0
    total_out = active.filter(amount__lt=0).aggregate(s=Sum('amount'))['s'] or 0

    if tx_type == 'in':
        transactions = transactions.filter(amount__gt=0)
    elif tx_type == 'out':
        transactions = transactions.filter(amount__lt=0)

    context = {
        'transactions': transactions,
        'date_from': str(date_from), 'date_to': str(date_to),
        'is_single_day': date_from == date_to,
        'tx_type': tx_type,
        'total_in': total_in, 'total_out': abs(total_out),
        'balance': total_in + total_out, 'active_page': 'transactions'
    }
    return render(request, 'transactions/list.html', context)

def transaction_create(request):
    if request.method == 'POST':
        amount = safe_decimal(request.POST.get('amount'))
        ttype = request.POST.get('type')
        if ttype == 'expense':
            amount = -abs(amount)
        employee_id = request.POST.get('employee') or None
        note = request.POST.get('note', '')
        tx = Transaction.objects.create(
            employee_id=employee_id,
            amount=amount,
            category=request.POST.get('category', 'other'),
            payment_type=request.POST.get('payment_type', 'cash'),
            note=note,
        )
        # Joriy balansni yangilash: kirim (musbat) qo'shiladi, chiqim (manfiy) ayriladi
        from warehouse.models import Balance
        Balance.add(amount)
        emp_name = tx.employee.name if tx.employee else "Belgilanmagan"
        kind = "💸 Xarajat" if amount < 0 else "💵 Kirim"
        text = f"""{kind} — Biznex
👤 Xodim: {emp_name}
💰 Summa: {abs(amount):,.0f} UZS
💳 To'lov turi: {tx.get_payment_type_display()}
📝 Izoh: {note or "—"}
🕒 {timezone.now().strftime('%d.%m.%Y %H:%M')}"""
        send_telegram(text)
        return redirect('transactions:list')
    employees = Employee.objects.filter(is_active=True)
    return render(request, 'transactions/form.html', {'employees': employees, 'active_page': 'transactions'})


def transaction_delete(request, pk):
    """Faqat 'bekor qilingan' (is_voided) tranzaksiyalarni Tranzaksiyalar ro'yxatidan
    butunlay o'chirish uchun — buyurtma o'chirilganda balansdan pul allaqachon ayirilgan,
    bu yerda faqat tarixdagi yozuv o'zi olib tashlanadi."""
    from django.http import JsonResponse
    tx = get_object_or_404(Transaction, pk=pk)
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST kerak'}, status=405)
    if not tx.is_voided:
        return JsonResponse({'success': False, 'error': "Faqat bekor qilingan tranzaksiyalarni o'chirish mumkin"}, status=400)
    tx.delete()
    return JsonResponse({'success': True})
