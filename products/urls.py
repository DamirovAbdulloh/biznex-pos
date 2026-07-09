from django.urls import path
from . import views, api
app_name = 'products'
urlpatterns = [
    # --- Vue SPA JSON API ---
    path('api/', api.product_list_api, name='api_list'),
    path('api/create/', api.product_create_api, name='api_create'),
    path('api/reorder/', api.product_reorder_api, name='api_reorder'),
    path('api/<int:pk>/edit/', api.product_edit_api, name='api_edit'),
    path('api/<int:pk>/delete/', api.product_delete_api, name='api_delete'),
    path('api/categories/', api.category_list_api, name='api_categories'),
    path('api/categories/create/', api.category_create_api, name='api_category_create'),
    path('api/categories/<int:pk>/edit/', api.category_edit_api, name='api_category_edit'),
    path('api/categories/<int:pk>/delete/', api.category_delete_api, name='api_category_delete'),

    path('', views.product_list, name='list'),
    path('create/', views.product_create, name='create'),
    path('reorder/', views.product_reorder, name='reorder'),
    path('<int:pk>/', views.product_detail, name='detail'),
    path('<int:pk>/edit/', views.product_edit, name='edit'),
    path('<int:pk>/delete/', views.product_delete, name='delete'),
    path('categories/', views.category_list, name='categories'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
