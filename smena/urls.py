from django.urls import path
from . import views

app_name = 'smena'

urlpatterns = [
    path('', views.smena_view, name='view'),
]
