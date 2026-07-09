from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta, date


def dashboard(request):
    from django.shortcuts import redirect
    if not request.session.get('admin_emp_id'):
        return redirect('employees:admin_pin_login')
    from orders.models import Order
    from products.models import Product, Category
    from employees.models import Employee
    from transactions.models import Transaction
    from locations.models import Location
    from clients.models import Client
    from warehouse.models import Balance

    today = timezone.now().date()

    # Sanadan-sanagacha (range) filtri. Eski `?date=` parametri bilan orqaga moslik
    # uchun ham qo'llab-quvvatlanadi (bitta kunni tanlash uchun).
    legacy_date_str = request.GET.get('date', '')
    date_from_str = request.GET.get('date_from', '')
    date_to_str = request.GET.get('date_to', '')

    if legacy_date_str and not date_from_str and not date_to_str:
        date_from_str = date_to_str = legacy_date_str

    def _parse(value, default):
        try:
            return date.fromisoformat(value)
        except (ValueError, TypeError):
            return default

    date_from = _parse(date_from_str, today)
    date_to = _parse(date_to_str, today)
    if date_from > date_to:
        date_from, date_to = date_to, date_from
    filter_date = date_to  # orqaga moslik uchun (ba'zi joylarda bitta sana sifatida ishlatiladi)

    tx_qs = Transaction.objects.filter(created_at__date__gte=date_from, created_at__date__lte=date_to).exclude(is_voided=True)
    order_qs = Order.objects.filter(created_at__date__gte=date_from, created_at__date__lte=date_to).exclude(status='deleted')
    closed_orders_today = order_qs.filter(status='closed').select_related().prefetch_related('orderitem_set__product')

    total_orders = order_qs.count()
    total_income = tx_qs.filter(amount__gt=0).aggregate(s=Sum('amount'))['s'] or 0
    total_expense = tx_qs.filter(amount__lt=0).aggregate(s=Sum('amount'))['s'] or 0

    # Sotilgan taomlarning jami tan narxi (faqat to'langan buyurtmalar)
    total_cost = sum(o.get_cost_total() for o in closed_orders_today)

    total_products = Product.objects.filter(is_active=True).count()
    total_employees = Employee.objects.filter(is_active=True).count()
    total_locations = Location.objects.count()
    total_clients = Client.objects.count()
    total_categories = Category.objects.count()
    total_cancels = Order.objects.filter(
        status='cancelled', created_at__date__gte=date_from, created_at__date__lte=date_to
    ).count()

    # Balans
    balance = Balance.get_balance()

    # Stats cards (clickable)
    from django.urls import reverse
    stats = [
        ('Hodimlar', total_employees, 'blue', reverse('employees:list')),
        ('Mahsulotlar', total_products, 'green', reverse('products:list')),
        ('Buyurtmalar', total_orders, 'purple', reverse('orders:list')),
        ('Kategoriyalar', total_categories, 'yellow', reverse('products:categories')),
        ('Mijozlar', total_clients, 'pink', reverse('clients:list')),
        ('Joylar', total_locations, 'indigo', reverse('locations:list')),
        ('Bekor qilishlar', total_cancels, 'red', reverse('orders:list') + '?status=cancelled'),
    ]

    recent_orders = Order.objects.exclude(status='deleted').select_related('table', 'employee').order_by('-created_at')[:10]

    # Xodimlar ish haqi
    num_days = (date_to - date_from).days + 1
    employees = Employee.objects.filter(is_active=True).select_related('role')
    employee_salaries = []
    total_salaries = 0
    for emp in employees:
        # Saboy buyurtmalardan komissiya hisoblanmaydi
        closed_orders = Order.objects.filter(
            employee=emp, status='closed', is_takeaway=False,
            created_at__date__gte=date_from, created_at__date__lte=date_to,
        )
        emp_total_sales = sum(o.get_total() for o in closed_orders)
        emp_commission = float(emp_total_sales) * float(emp.commission_percent) / 100
        emp_orders_count = closed_orders.count()
        role_name = emp.role.name.lower() if emp.role else ''
        # Oshpaz — oylik, Ofitsant — kunlik + komissiya (tanlangan davrdagi kunlar soniga ko'paytiriladi)
        if 'ofitsant' in role_name or 'waiter' in role_name:
            total_earnings = emp_commission + float(emp.daily_rate) * num_days
            salary_type = 'kunlik'
        else:
            total_earnings = float(emp.monthly_rate)
            salary_type = 'oylik'
        total_salaries += total_earnings
        employee_salaries.append({
            'emp': emp,
            'total_sales': emp_total_sales,
            'commission': emp_commission,
            'orders_count': emp_orders_count,
            'daily_rate': float(emp.daily_rate),
            'monthly_rate': float(emp.monthly_rate),
            'total_earnings': total_earnings,
            'salary_type': salary_type,
        })

    # Haqiqiy sof foyda = Jami kirim - Taomlarning tan narxi - Xodimlar ish haqi (komissiya + stavka)
    net_profit = float(total_income) - float(total_cost) - float(total_salaries)
    total_cost_and_salaries = float(total_cost) + float(total_salaries)

    context = {
        'total_orders': total_orders,
        'total_income': total_income,
        'total_expense': abs(total_expense or 0),
        'total_cost': total_cost,
        'total_salaries': total_salaries,
        'total_cost_and_salaries': total_cost_and_salaries,
        'net_profit': net_profit,
        'total_products': total_products,
        'total_employees': total_employees,
        'total_locations': total_locations,
        'total_clients': total_clients,
        'total_categories': total_categories,
        'total_cancels': total_cancels,
        'stats': stats,
        'recent_orders': recent_orders,
        'filter_date': filter_date,
        'date_from': date_from,
        'date_to': date_to,
        'is_single_day': date_from == date_to,
        'today': today,
        'active_page': 'reports',
        'employee_salaries': employee_salaries,
        'balance': balance,
    }
    return render(request, 'reports/dashboard.html', context)


def _products_report_rows(date_from, date_to=None):
    """Berilgan sana (yoki sanadan-sanagacha oraliq) uchun barcha faol taomlarning
    sotuv statistikasini hisoblaydi: tan narx, sotish narxi, sotilgan soni, kirim, sof foyda."""
    from products.models import Product
    if date_to is None:
        date_to = date_from
    products = Product.objects.filter(is_active=True).order_by('order', 'id')
    rows = []
    totals = {'income': 0, 'cost': 0, 'profit': 0, 'qty': 0}
    for p in products:
        stats = p.get_sales_stats(date_from=date_from, date_to=date_to)
        row = {
            'id': p.pk,
            'name': p.name,
            'cost_price': float(p.cost_price),
            'price': float(p.price),
            'qty': float(stats['total_qty']),
            'income': float(stats['total_income']),
            'cost': float(stats['total_cost']),
            'profit': float(stats['net_profit']),
        }
        rows.append(row)
        totals['income'] += row['income']
        totals['cost'] += row['cost']
        totals['profit'] += row['profit']
        totals['qty'] += row['qty']
    rows.sort(key=lambda r: r['profit'], reverse=True)
    return rows, totals


def products_report_data(request):
    """Hisobotlar sahifasidagi 'Mahsulotlar' kartasi bosilganda ochiladigan
    oynani to'ldirish uchun JSON — har bir taomning tan narxi, sotish narxi,
    sotilgan soni, kirim va sof foydasi."""
    from django.http import JsonResponse
    from datetime import date as date_cls
    today = timezone.now().date()

    def _parse(value, default):
        try:
            return date_cls.fromisoformat(value) if value else default
        except ValueError:
            return default

    legacy_date_str = request.GET.get('date', '')
    date_from_str = request.GET.get('date_from', '') or legacy_date_str
    date_to_str = request.GET.get('date_to', '') or legacy_date_str

    date_from = _parse(date_from_str, today)
    date_to = _parse(date_to_str, today)
    if date_from > date_to:
        date_from, date_to = date_to, date_from

    rows, totals = _products_report_rows(date_from, date_to)
    return JsonResponse({
        'date_from': str(date_from), 'date_to': str(date_to),
        'rows': rows, 'totals': totals,
    })


def products_report_print(request):
    """Mahsulotlar hisobotining chop etish/PDF sifatida saqlash uchun sahifasi."""
    from datetime import date as date_cls
    today = timezone.now().date()

    def _parse(value, default):
        try:
            return date_cls.fromisoformat(value) if value else default
        except ValueError:
            return default

    legacy_date_str = request.GET.get('date', '')
    date_from_str = request.GET.get('date_from', '') or legacy_date_str
    date_to_str = request.GET.get('date_to', '') or legacy_date_str

    date_from = _parse(date_from_str, today)
    date_to = _parse(date_to_str, today)
    if date_from > date_to:
        date_from, date_to = date_to, date_from

    rows, totals = _products_report_rows(date_from, date_to)
    return render(request, 'reports/products_report_print.html', {
        'rows': rows, 'totals': totals,
        'filter_date': date_to, 'date_from': date_from, 'date_to': date_to,
        'is_single_day': date_from == date_to,
    })
