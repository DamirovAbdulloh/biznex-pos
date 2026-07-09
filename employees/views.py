from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Employee, Role
from biznex.utils import safe_decimal


# ========== UNIVERSAL PIN LOGIN (barcha xodimlar uchun) ==========

def _route_employee_login(request, emp):
    """PIN mos kelgan xodimni roliga qarab tegishli panelga yo'naltiradi.
    Sessionni o'rnatadi va redirect javobini qaytaradi; rol aniqlanmasa None qaytaradi."""
    role_name = emp.role.name.lower() if emp.role else ''

    if 'admin' in role_name or 'kassir' in role_name or 'manager' in role_name:
        request.session['admin_emp_id'] = emp.pk
        request.session['admin_emp_name'] = emp.name
        request.session['admin_emp_role'] = emp.role.name if emp.role else ''
        return redirect('reports:dashboard')
    elif 'oshpaz' in role_name or 'cook' in role_name:
        request.session['waiter_id'] = emp.pk
        request.session['waiter_name'] = emp.name
        request.session['waiter_role'] = emp.role.name if emp.role else ''
        return redirect('orders:kitchen')
    elif 'ofitsiant' in role_name or 'ofitsant' in role_name or 'waiter' in role_name:
        request.session['waiter_id'] = emp.pk
        request.session['waiter_name'] = emp.name
        request.session['waiter_role'] = emp.role.name if emp.role else ''
        return redirect('employees:waiter_orders')
    return None


def admin_pin_login(request):
    """Bitta login sahifasi — barcha xodimlar uchun (admin, kassir, ofitsant, oshpaz)"""
    error = None
    if request.method == 'POST':
        pin = request.POST.get('pin', '').strip()
        try:
            emp = Employee.objects.get(pin_code=pin, is_active=True)
            redirect_response = _route_employee_login(request, emp)
            if redirect_response:
                return redirect_response
            error = "Rolingiz aniqlanmadi. Admin bilan bog'laning."
        except Employee.DoesNotExist:
            error = "PIN kod noto'g'ri yoki xodim topilmadi"
    return render(request, 'employees/admin_pin_login.html', {'error': error})


def panel_select(request):
    """Panellar — barcha faol xodimlar ro'yxati (rasm bo'yicha kartalar).
    Xodim tanlansa, o'sha xodimning PIN kodini kiritish ekraniga o'tadi."""
    employees = Employee.objects.filter(is_active=True).select_related('role').order_by('name')
    return render(request, 'employees/panel_select.html', {'employees': employees})


def panel_pin_entry(request, pk):
    """Tanlangan xodim uchun PIN kiritish — faqat shu xodimning kodi qabul qilinadi."""
    employee = get_object_or_404(Employee, pk=pk, is_active=True)
    error = None
    if request.method == 'POST':
        pin = request.POST.get('pin', '').strip()
        if pin and employee.pin_code == pin:
            redirect_response = _route_employee_login(request, employee)
            if redirect_response:
                return redirect_response
            error = "Rolingiz aniqlanmadi. Admin bilan bog'laning."
        else:
            error = "PIN kod noto'g'ri"
    return render(request, 'employees/panel_pin_login.html', {'employee': employee, 'error': error})


def admin_pin_logout(request):
    request.session.pop('admin_emp_id', None)
    request.session.pop('admin_emp_name', None)
    request.session.pop('admin_emp_role', None)
    return redirect('employees:admin_pin_login')


# ========== EMPLOYEE CRUD ==========

def employee_list(request):
    employees = Employee.objects.filter(is_active=True).select_related('role')
    roles = Role.objects.all()
    return render(request, 'employees/list.html', {'employees': employees, 'roles': roles, 'active_page': 'employees'})


def employee_create(request):
    if request.method == 'POST':
        from django.contrib import messages
        from django.db import IntegrityError
        new_role_name = request.POST.get('new_role_name', '').strip()
        if new_role_name:
            role, _ = Role.objects.get_or_create(name=new_role_name)
            role_id = role.pk
        else:
            role_id = request.POST.get('role') or None

        pin_code = request.POST.get('pin_code', '').strip() or None
        if pin_code and Employee.objects.filter(pin_code=pin_code).exists():
            messages.error(request, f"\"{pin_code}\" PIN kodi boshqa xodimda allaqachon band. Boshqa PIN tanlang.")
            roles = Role.objects.all()
            return render(request, 'employees/form.html', {'roles': roles, 'active_page': 'employees'})

        try:
            Employee.objects.create(
                name=request.POST.get('name', '').strip() or 'Nomsiz xodim',
                role_id=role_id,
                phone=request.POST.get('phone', ''),
                pin_code=pin_code,
                commission_percent=safe_decimal(request.POST.get('commission_percent')),
                daily_rate=safe_decimal(request.POST.get('daily_rate')),
                monthly_rate=safe_decimal(request.POST.get('monthly_rate')),
            )
        except IntegrityError:
            messages.error(request, "Bu PIN kodi band. Boshqa PIN tanlang.")
            roles = Role.objects.all()
            return render(request, 'employees/form.html', {'roles': roles, 'active_page': 'employees'})
        return redirect('employees:list')
    roles = Role.objects.all()
    return render(request, 'employees/form.html', {'roles': roles, 'active_page': 'employees'})


def employee_edit(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        from django.contrib import messages
        from django.db import IntegrityError
        new_role_name = request.POST.get('new_role_name', '').strip()
        if new_role_name:
            role, _ = Role.objects.get_or_create(name=new_role_name)
            emp.role_id = role.pk
        else:
            emp.role_id = request.POST.get('role') or None
        emp.name = request.POST.get('name', '').strip() or emp.name
        emp.phone = request.POST.get('phone', '')
        pin = request.POST.get('pin_code', '').strip()
        if pin and pin != emp.pin_code:
            if Employee.objects.filter(pin_code=pin).exclude(pk=emp.pk).exists():
                messages.error(request, f"\"{pin}\" PIN kodi boshqa xodimda allaqachon band. Boshqa PIN tanlang.")
                roles = Role.objects.all()
                return render(request, 'employees/form.html', {'emp': emp, 'roles': roles, 'active_page': 'employees'})
            emp.pin_code = pin
        emp.commission_percent = safe_decimal(request.POST.get('commission_percent'))
        emp.daily_rate = safe_decimal(request.POST.get('daily_rate'))
        emp.monthly_rate = safe_decimal(request.POST.get('monthly_rate'))
        try:
            emp.save()
        except IntegrityError:
            messages.error(request, "Bu PIN kodi band. Boshqa PIN tanlang.")
            roles = Role.objects.all()
            return render(request, 'employees/form.html', {'emp': emp, 'roles': roles, 'active_page': 'employees'})
        return redirect('employees:list')
    roles = Role.objects.all()
    return render(request, 'employees/form.html', {'emp': emp, 'roles': roles, 'active_page': 'employees'})


def employee_delete(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    emp.is_active = False
    emp.save()
    return redirect('employees:list')


def employee_detail_api(request, pk):
    """Xodim malumotlari modal uchun JSON"""
    emp = get_object_or_404(Employee, pk=pk, is_active=True)
    from django.utils import timezone
    from orders.models import Order
    today = timezone.now().date()
    month = timezone.now().month
    year = timezone.now().year

    role_name = emp.role.name.lower() if emp.role else ''

    # Bugungi
    today_orders = Order.objects.filter(employee=emp, status='closed', created_at__date=today)
    today_sales = sum(o.get_total() for o in today_orders)
    today_commission = float(today_sales) * float(emp.commission_percent) / 100

    # Oylik
    month_orders = Order.objects.filter(employee=emp, status='closed',
                                        created_at__year=year, created_at__month=month)
    month_sales = sum(o.get_total() for o in month_orders)
    month_commission = float(month_sales) * float(emp.commission_percent) / 100

    # Ofitsant: kunlik + komissiya. Oshpaz/admin: oylik
    if 'ofitsant' in role_name or 'waiter' in role_name:
        today_earnings = today_commission + float(emp.daily_rate)
        month_earnings = month_commission + float(emp.monthly_rate)
        salary_type = 'kunlik'
    else:
        today_earnings = float(emp.monthly_rate)  # oshpaz oylik
        month_earnings = float(emp.monthly_rate)
        salary_type = 'oylik'

    # Ish haqi tarixi
    history = []
    if salary_type == 'kunlik':
        from datetime import timedelta
        for i in range(13, -1, -1):  # oxirgi 14 kun, eskisidan yangisiga
            d = today - timedelta(days=i)
            day_orders = Order.objects.filter(employee=emp, status='closed', created_at__date=d)
            day_sales = float(sum(o.get_total() for o in day_orders))
            day_commission = day_sales * float(emp.commission_percent) / 100
            history.append({
                'label': d.strftime('%d.%m'),
                'sales': day_sales,
                'commission': day_commission,
                'earnings': day_commission + float(emp.daily_rate),
                'orders_count': day_orders.count(),
            })
    else:
        for i in range(5, -1, -1):  # oxirgi 6 oy, eskisidan yangisiga
            m = month - i
            y = year
            while m <= 0:
                m += 12
                y -= 1
            mon_orders = Order.objects.filter(employee=emp, status='closed', created_at__year=y, created_at__month=m)
            mon_sales = float(sum(o.get_total() for o in mon_orders))
            oy_nomlari = ['', 'Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyun', 'Iyul', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek']
            history.append({
                'label': f"{oy_nomlari[m]} {y}",
                'sales': mon_sales,
                'commission': 0,
                'earnings': float(emp.monthly_rate),
                'orders_count': mon_orders.count(),
            })

    data = {
        'id': emp.pk,
        'name': emp.name,
        'role': emp.role.name if emp.role else '—',
        'phone': emp.phone or '—',
        'pin_code': emp.pin_code or '—',
        'commission_percent': float(emp.commission_percent),
        'daily_rate': float(emp.daily_rate),
        'monthly_rate': float(emp.monthly_rate),
        'today_sales': float(today_sales),
        'today_commission': today_commission,
        'today_earnings': today_earnings,
        'month_sales': float(month_sales),
        'month_commission': month_commission,
        'month_earnings': month_earnings,
        'today_orders_count': today_orders.count(),
        'month_orders_count': month_orders.count(),
        'salary_type': salary_type,
        'history': history,
        'created_at': emp.created_at.strftime('%d.%m.%Y'),
        'is_active': emp.is_active,
    }
    return JsonResponse(data)


def role_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            role, created = Role.objects.get_or_create(name=name)
            return JsonResponse({'id': role.pk, 'name': role.name, 'created': created})
        return JsonResponse({'error': "Nomi bo'sh"}, status=400)
    return JsonResponse({'error': 'Faqat POST'}, status=405)


# ========== WAITER PANEL ==========

def waiter_login(request):
    """Ofitsant/Oshpaz login — universal login sahifasiga yo'naltiradi"""
    return redirect('employees:admin_pin_login')


def waiter_logout(request):
    request.session.pop('waiter_id', None)
    request.session.pop('waiter_name', None)
    request.session.pop('waiter_role', None)
    return redirect('employees:admin_pin_login')


def waiter_tables(request):
    waiter_id = request.session.get('waiter_id')
    if not waiter_id:
        return redirect('employees:admin_pin_login')
    from locations.models import Table, Location
    waiter = get_object_or_404(Employee, pk=waiter_id, is_active=True)
    locations = Location.objects.prefetch_related('table_set').all()
    return render(request, 'employees/waiter_tables.html', {
        'waiter': waiter,
        'locations': locations,
    })


def waiter_orders(request):
    """Ofitsantning xizmat ko'rsatgan stollaridagi, mijoz hali to'lamagan buyurtmalar"""
    waiter_id = request.session.get('waiter_id')
    if not waiter_id:
        return redirect('employees:admin_pin_login')
    from orders.models import Order
    waiter = get_object_or_404(Employee, pk=waiter_id, is_active=True)
    orders = Order.objects.filter(
        employee=waiter, status='open', is_paid=False
    ).select_related('table').prefetch_related('orderitem_set__product').order_by('-created_at')
    return render(request, 'employees/waiter_orders.html', {
        'waiter': waiter,
        'orders': orders,
    })
