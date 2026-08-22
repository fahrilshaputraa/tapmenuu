from django.contrib import admin

from payments.models import Payment, RestaurantPaymentConfig


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'reference',
        'order',
        'method',
        'amount',
        'status',
        'provider',
        'paid_at',
        'created_at',
    )
    list_filter = ('method', 'status', 'provider', 'created_at', 'paid_at')
    search_fields = (
        'reference',
        'provider_reference',
        'order__code',
        'order__customer_name',
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(RestaurantPaymentConfig)
class RestaurantPaymentConfigAdmin(admin.ModelAdmin):
    list_display = (
        'restaurant',
        'gateway',
        'is_active',
        'midtrans_is_production',
        'updated_at',
    )
    list_filter = ('gateway', 'is_active', 'midtrans_is_production')
    search_fields = ('restaurant__name', 'restaurant__slug')
    readonly_fields = (
        'midtrans_server_key_encrypted',
        'midtrans_client_key_encrypted',
        'created_at',
        'updated_at',
    )
