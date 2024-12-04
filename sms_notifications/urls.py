# flash_sale_project/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('create-sale/', views.create_sale, name='create_sale'),
]