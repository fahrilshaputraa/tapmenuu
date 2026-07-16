from uuid import uuid4

from django.db import transaction
from django.utils import timezone

from orders.models import Order, OrderItem


class OrderCreationError(ValueError):
    """Raised when an order cannot be created from cart data."""


def create_order_from_cart(*, table, cart_items, customer_name='', customer_note=''):
    """Create an order and order item snapshots from cart data.

    cart_items format:
    [
        {'menu_item': MenuItem, 'quantity': 2, 'note': 'tanpa pedas'},
    ]
    """
    if not cart_items:
        raise OrderCreationError('Cart tidak boleh kosong.')

    with transaction.atomic():
        order = Order.objects.create(
            restaurant=table.restaurant,
            dining_table=table,
            code=_generate_order_code(),
            customer_name=customer_name,
            notes=customer_note,
        )

        total_amount = 0
        for cart_item in cart_items:
            menu_item = cart_item['menu_item']
            quantity = int(cart_item.get('quantity', 1))
            note = cart_item.get('note', '')
            unit_price = int(cart_item.get('unit_price', menu_item.price))

            if quantity < 1:
                raise OrderCreationError('Quantity menu minimal 1.')

            if menu_item.restaurant_id != table.restaurant_id:
                raise OrderCreationError(
                    'Menu harus berasal dari restoran meja yang sama.',
                )

            if not menu_item.is_active or not menu_item.is_available:
                raise OrderCreationError(
                    f'Menu {menu_item.name} sedang tidak tersedia.',
                )

            order_item = OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                item_name=menu_item.name,
                unit_price=unit_price,
                quantity=quantity,
                notes=note,
            )
            total_amount += order_item.line_total

        order.total_amount = total_amount
        order.save(update_fields=['total_amount', 'updated_at'])
        return order


def _generate_order_code():
    today = timezone.localdate().strftime('%Y%m%d')
    suffix = uuid4().hex[:8].upper()
    return f'ORD-{today}-{suffix}'
