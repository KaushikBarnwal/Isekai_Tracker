from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('inventory/', views.inventory_page, name='inventory'),
    path('equip/<int:inventory_id>/', views.toggle_equip, name='toggle_equip'),
]
