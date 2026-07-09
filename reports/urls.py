from django.urls import path
from . import views
app_name = 'reports'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products-report/', views.products_report_data, name='products_report_data'),
    path('products-report/print/', views.products_report_print, name='products_report_print'),
]
