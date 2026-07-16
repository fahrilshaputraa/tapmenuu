from django.urls import path

from menus import views

urlpatterns = [
    path('m/<slug:qr_token>/', views.customer_menu, name='customer_menu'),
    path('m/<slug:qr_token>/cart/', views.customer_cart, name='customer_cart'),
    path(
        'm/<slug:qr_token>/cart/add/<int:item_id>/',
        views.customer_cart_add,
        name='customer_cart_add',
    ),
    path(
        'm/<slug:qr_token>/cart/quantity/<path:line_key>/',
        views.customer_cart_quantity,
        name='customer_cart_quantity',
    ),
    path(
        'm/<slug:qr_token>/cart/remove/<path:line_key>/',
        views.customer_cart_remove,
        name='customer_cart_remove',
    ),
    path(
        'm/<slug:qr_token>/checkout/',
        views.customer_checkout,
        name='customer_checkout',
    ),
    path(
        'm/<slug:qr_token>/orders/<int:order_id>/success/',
        views.customer_order_success,
        name='customer_order_success',
    ),
]
