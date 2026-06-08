"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/menus/', views.management_menu, name='management_menu'),
    path('dashboard/store/', views.store, name='store'),
    path('dashboard/orders/', views.orders, name='orders'),
    path('dashboard/employees/', views.employee, name='employee'),
    path('dashboard/reports/', views.reports, name='reports'),
    path('dashboard/tables/', views.tables, name='tables'),
    path('menu/', views.book_menu, name='book_menu'),
    path('', include('menus.urls')),
    path('admin/', admin.site.urls),
]
