from django.urls import path
from . import views

app_name = 'locations'

urlpatterns = [
    path('', views.location_list, name='list'),
    path('<int:pk>/delete/', views.location_delete, name='delete'),
    path('<int:pk>/tables/', views.table_list, name='tables'),
]
