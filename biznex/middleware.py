from django.shortcuts import redirect
from django.urls import reverse
import re

# Admin panelga kirish uchun session tekshiruvchi sahifalar
ADMIN_PROTECTED = [
    '/orders/', '/products/', '/employees/', '/reports/',
    '/locations/', '/transactions/', '/clients/', '/smena/', '/warehouse/', '/settings/',
    '/app/',
]

# Bu URL larga login kerak emas
PUBLIC_URLS = [
    '/employees/admin-login/',
    '/employees/admin-logout/',
    '/employees/waiter/',
    '/employees/waiter/logout/',
    '/employees/panels/',
    '/admin/',
]

# Ofitsant/Oshpaz paneli URL lari — alohida session (waiter_id YOKI admin_emp_id kifoya)
WAITER_URLS = [
    '/employees/waiter/',
    '/orders/kitchen',
    '/orders/pos-waiter',
]

# Buyurtma tarkibini o'zgartiruvchi AJAX endpointlar — ofitsant POS sahifasidan chaqiriladi,
# shuning uchun waiter_id sessiyasi ham yetarli bo'lishi kerak (faqat admin_emp_id emas)
ORDER_MUTATION_RE = re.compile(
    r'^/orders/\d+/(add-item|update-qty|remove-item|send-kitchen|kitchen-ready)/$'
)


class AdminAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Public URL lar — tekshiruvsiz o'tkazamiz
        for pub in PUBLIC_URLS:
            if path.startswith(pub):
                return self.get_response(request)

        # Kitchen va waiter_pos — waiter session tekshiramiz
        if path.startswith('/orders/kitchen') or path.startswith('/orders/pos-waiter') or path.startswith('/employees/waiter/tables') or path.startswith('/employees/waiter/orders'):
            if not request.session.get('waiter_id'):
                return redirect('employees:admin_pin_login')
            return self.get_response(request)

        # Buyurtma tarkibini o'zgartiruvchi AJAX so'rovlar — ofitsant (waiter_id) YOKI admin/kassir (admin_emp_id)
        if ORDER_MUTATION_RE.match(path):
            if request.session.get('waiter_id') or request.session.get('admin_emp_id'):
                return self.get_response(request)
            return redirect('employees:admin_pin_login')

        # Admin protected URL lar
        for prot in ADMIN_PROTECTED:
            if path.startswith(prot):
                if not request.session.get('admin_emp_id'):
                    return redirect('employees:admin_pin_login')
                break

        return self.get_response(request)
