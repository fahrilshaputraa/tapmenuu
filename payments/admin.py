from django.contrib import admin

from payments.models import Payment


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
