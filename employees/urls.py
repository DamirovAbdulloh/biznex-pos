from django.urls import path
from . import views
app_name = 'employees'
urlpatterns = [
    path('', views.employee_list, name='list'),
    path('create/', views.employee_create, name='create'),
    path('<int:pk>/edit/', views.employee_edit, name='edit'),
    path('<int:pk>/delete/', views.employee_delete, name='delete'),
    path('<int:pk>/detail/', views.employee_detail_api, name='detail_api'),
    path('role/create/', views.role_create, name='role_create'),
    # Admin PIN login
    path('admin-login/', views.admin_pin_login, name='admin_pin_login'),
    path('admin-logout/', views.admin_pin_logout, name='admin_pin_logout'),
    # Panellar — xodim tanlab kirish
    path('panels/', views.panel_select, name='panel_select'),
    path('panels/<int:pk>/login/', views.panel_pin_entry, name='panel_pin_entry'),
    # Waiter panel
    path('waiter/', views.waiter_login, name='waiter_login'),
    path('waiter/logout/', views.waiter_logout, name='waiter_logout'),
    path('waiter/tables/', views.waiter_tables, name='waiter_tables'),
    path('waiter/orders/', views.waiter_orders, name='waiter_orders'),
]
