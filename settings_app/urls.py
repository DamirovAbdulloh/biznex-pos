from django.urls import path
from . import views

app_name = 'settings_app'
urlpatterns = [
    path('', views.settings_view, name='settings'),
    path('sync-now/', views.sync_now_view, name='sync_now'),
]
