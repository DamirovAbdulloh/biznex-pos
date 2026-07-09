from django.urls import path
from . import views

app_name = 'warehouse'

urlpatterns = [
    path('', views.warehouse_list, name='list'),
    path('add/', views.warehouse_add, name='add'),
    path('<int:pk>/delete/', views.warehouse_delete, name='delete'),
    path('topup/', views.balance_topup, name='topup'),
]
