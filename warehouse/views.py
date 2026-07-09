from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import WarehouseItem, Balance
from django.db.models import Sum


def warehouse_list(request):
    items = WarehouseItem.objects.all()
    total_spent = items.aggregate(s=Sum('total_cost'))['s'] or 0
    balance = Balance.get_balance()
    context = {
        'items': items,
        'total_spent': total_spent,
        'balance': balance,
        'active_page': 'warehouse',
    }
    return render(request, 'warehouse/list.html', context)


def warehouse_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        unit = request.POST.get('unit', 'dona').strip()
        note = request.POST.get('note', '').strip()

        try:
            quantity = Decimal(request.POST.get('quantity', '1') or '1')
        except InvalidOperation:
            quantity = Decimal('1')

        try:
            price_per_unit = Decimal(request.POST.get('price_per_unit', '0') or '0')
        except InvalidOperation:
            price_per_unit = Decimal('0')

        WarehouseItem.objects.create(
            name=name,
            quantity=quantity,
            unit=unit,
            price_per_unit=price_per_unit,
            note=note,
        )
        return redirect('warehouse:list')
    return redirect('warehouse:list')


def warehouse_delete(request, pk):
    item = get_object_or_404(WarehouseItem, pk=pk)
    # Balansga qaytarish
    Balance.add(item.total_cost)
    item.delete()
    return redirect('warehouse:list')


def balance_topup(request):
    """Balansni to'ldirish (admin uchun)"""
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0') or '0')
        except InvalidOperation:
            amount = Decimal('0')
        if amount > 0:
            Balance.add(amount)
    return redirect('warehouse:list')
