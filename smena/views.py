from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum
from .models import Smena
from transactions.models import Transaction
from biznex.utils import send_telegram

def smena_view(request):
    today = timezone.now().date()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'open':
            if not Smena.objects.filter(status='open').exists():
                Smena.objects.create()
                send_telegram(
                    f"🟢 <b>Smena ochildi</b>\n🕒 {timezone.now().strftime('%d.%m.%Y %H:%M')}"
                )
        elif action == 'close':
            smena = Smena.objects.filter(status='open').first()
            if smena:
                smena.status = 'closed'
                smena.closed_at = timezone.now()
                smena.save()
                today_tx = Transaction.objects.filter(created_at__date=today)
                sales_amount = today_tx.filter(amount__gt=0).aggregate(s=Sum('amount'))['s'] or 0
                returns_amount = abs(today_tx.filter(amount__lt=0).aggregate(s=Sum('amount'))['s'] or 0)
                send_telegram(
                    f"🔴 <b>Smena yopildi</b>\n"
                    f"💰 Kirim: {sales_amount:,.0f} UZS\n"
                    f"↩️ Chiqim/qaytarma: {returns_amount:,.0f} UZS\n"
                    f"📊 Sof: {sales_amount - returns_amount:,.0f} UZS\n"
                    f"🕒 {timezone.now().strftime('%d.%m.%Y %H:%M')}"
                )
        return redirect('smena:view')

    smena = Smena.objects.filter(status='open').first()

    # Today's transactions
    today_tx = Transaction.objects.filter(created_at__date=today)
    sales_count = today_tx.filter(amount__gt=0).count()
    sales_amount = today_tx.filter(amount__gt=0).aggregate(s=Sum('amount'))['s'] or 0
    returns_count = today_tx.filter(amount__lt=0).count()
    returns_amount = abs(today_tx.filter(amount__lt=0).aggregate(s=Sum('amount'))['s'] or 0)
    net_income = sales_amount - returns_amount

    recent_checks = today_tx.order_by('-created_at')[:10]

    context = {
        'smena': smena,
        'today': today,
        'sales_count': sales_count,
        'sales_amount': sales_amount,
        'returns_count': returns_count,
        'returns_amount': returns_amount,
        'net_income': net_income,
        'recent_checks': recent_checks,
        'active_page': 'smena',
    }
    return render(request, 'smena/smena.html', context)
