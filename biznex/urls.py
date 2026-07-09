from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda r: redirect('employees:admin_pin_login'), name='home'),
    path('orders/', include('orders.urls')),
    path('products/', include('products.urls')),
    path('employees/', include('employees.urls')),
    path('login/', lambda r: redirect('employees:admin_pin_login'), name='login'),
    path('reports/', include('reports.urls')),
    path('locations/', include('locations.urls')),
    path('transactions/', include('transactions.urls')),
    path('clients/', include('clients.urls')),
    path('smena/', include('smena.urls')),
    path('warehouse/', include('warehouse.urls')),
    path('settings/', include('settings_app.urls')),
    path('sync/', include('syncing.urls')),

    # --- Vue SPA (yangi, tezkor navigatsiya) ---
    # SolidJS mikro-router History API orqali ishlaydi, shuning uchun /app/ ostidagi
    # BARCHA yo'llar bir xil shell HTML'ni qaytarishi kerak (masalan, sahifani
    # to'g'ridan-to'g'ri /app/orders/5 dan yangilasa ham ishlashi uchun).
    re_path(r'^app(?:/.*)?$', TemplateView.as_view(template_name='spa.html'), name='spa'),
]
