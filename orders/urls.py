from django.urls import path
from . import views, api
app_name = 'orders'
urlpatterns = [
    # --- Vue SPA JSON API ---
    path('api/', api.order_list_api, name='api_list'),
    path('api/<int:pk>/', api.order_detail_api, name='api_detail'),
    path('api/<int:pk>/mark-paid/', api.order_mark_paid_api, name='api_mark_paid'),
    path('api/<int:pk>/delete/', api.order_delete_api, name='api_delete'),

    path('', views.order_list, name='list'),
    path('create/', views.order_create, name='create'),
    path('receipt/preview/', views.receipt_preview, name='receipt_preview'),
    path('<int:pk>/', views.order_detail, name='detail'),
    path('<int:pk>/add-item/', views.add_item, name='add_item'),
    path('<int:pk>/update-qty/', views.update_item_qty, name='update_qty'),
    path('<int:pk>/remove-item/', views.remove_item, name='remove_item'),
    path('<int:pk>/close/', views.close_order, name='close'),
    path('<int:pk>/mark-paid/', views.mark_paid, name='mark_paid'),
    path('<int:pk>/closed-update-qty/', views.closed_update_qty, name='closed_update_qty'),
    path('<int:pk>/delete/', views.delete_order, name='delete'),
    path('<int:pk>/receipt/', views.receipt_view, name='receipt'),
    path('<int:pk>/send-kitchen/', views.waiter_send_to_kitchen, name='send_kitchen'),
    path('<int:pk>/kitchen-ready/', views.kitchen_mark_ready, name='kitchen_ready'),
    path('pos/<int:table_id>/', views.pos_view, name='pos'),
    path('pos-takeaway/<int:pk>/', views.pos_takeaway, name='pos_takeaway'),
    path('pos-waiter/', views.waiter_pos, name='waiter_pos'),
    path('kitchen/', views.kitchen_view, name='kitchen'),
    path('send-daily-report/', views.send_daily_report, name='send_daily_report'),
]
