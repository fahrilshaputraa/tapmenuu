from django.urls import path

from payments import views

urlpatterns = [
    path(
        'dummy-success/<str:reference>/',
        views.dummy_success,
        name='payment_dummy_success',
    ),
    path('webhook/', views.webhook, name='payment_webhook'),
]
