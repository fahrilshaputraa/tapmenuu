from django.urls import path

from dashboard import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard'),
    path('store/', views.store, name='store'),
    path('appearance/', views.menu_appearance, name='menu_appearance'),
    path('tables/', views.tables, name='tables'),
    path('tables/create/', views.table_create, name='table_create'),
    path('tables/<int:pk>/update/', views.table_update, name='table_update'),
    path('tables/<int:pk>/delete/', views.table_delete, name='table_delete'),
    path('menus/', views.management_menu, name='management_menu'),
    path('menus/categories/create/', views.category_create, name='category_create'),
    path(
        'menus/categories/<int:pk>/update/',
        views.category_update,
        name='category_update',
    ),
    path(
        'menus/categories/<int:pk>/delete/',
        views.category_delete,
        name='category_delete',
    ),
    path('menus/items/create/', views.menu_item_create, name='menu_item_create'),
    path(
        'menus/items/<int:pk>/update/',
        views.menu_item_update,
        name='menu_item_update',
    ),
    path(
        'menus/items/<int:pk>/variants/',
        views.menu_item_variants_json,
        name='menu_item_variants_json',
    ),
    path(
        'menus/items/<int:pk>/delete/',
        views.menu_item_delete,
        name='menu_item_delete',
    ),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path(
        'orders/<int:pk>/status/',
        views.order_update_status,
        name='order_update_status',
    ),
    path('reports/', views.reports, name='reports'),
    path('employees/', views.employee, name='employee'),
    path('categories/', views.category_management, name='category_management'),
]
