from django.contrib import admin

from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('created_at', 'line_total')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'restaurant',
        'dining_table',
        'customer_name',
        'status',
        'payment_status',
        'total_amount',
        'created_at',
    )
    list_filter = ('restaurant', 'status', 'payment_status', 'created_at')
    search_fields = (
        'code',
        'customer_name',
        'restaurant__name',
        'dining_table__table_number',
    )
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'item_name',
        'quantity',
        'unit_price',
        'line_total',
        'created_at',
    )
    list_filter = ('order__restaurant', 'created_at')
    search_fields = ('order__code', 'item_name', 'menu_item__name')
    readonly_fields = ('created_at', 'line_total')
