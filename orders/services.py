from uuid import uuid4

from django.db import transaction
from django.utils import timezone

from orders.models import Order, OrderItem


class OrderCreationError(ValueError):
    """Raised when an order cannot be created from cart data."""


class OrderStatusTransitionError(ValueError):
    """Raised when an order status transition is not allowed."""


# Allowed transitions for the order status state machine.
# new → paid → processing → ready → completed
# Cancellable from new and processing only.
ORDER_STATUS_TRANSITIONS: dict[str, set[str]] = {
    Order.Status.NEW: {
        Order.Status.PAID,
        Order.Status.PROCESSING,
        Order.Status.CANCELLED,
    },
    Order.Status.PAID: {Order.Status.PROCESSING},
    Order.Status.PROCESSING: {Order.Status.READY, Order.Status.CANCELLED},
    Order.Status.READY: {Order.Status.COMPLETED},
    Order.Status.COMPLETED: set(),
    Order.Status.CANCELLED: set(),
}


@transaction.atomic
def transition_order_status(*, order: Order, new_status: str) -> Order:
    """Enforce the order status state machine.

    Args:
        order: The Order instance to transition.
        new_status: The target status value (e.g. 'processing').

    Returns:
        The saved Order instance with the new status.

    Raises:
        OrderStatusTransitionError: If the transition is not allowed.
    """
    valid_statuses = Order.Status.values
    if new_status not in valid_statuses:
        raise OrderStatusTransitionError(
            f'Status "{new_status}" bukan status yang valid. '
            f'Pilihan: {", ".join(valid_statuses)}.',
        )

    allowed = ORDER_STATUS_TRANSITIONS.get(order.status, set())
    if new_status not in allowed:
        # Build a helpful error message with allowed next statuses.
        if allowed:
            labels = [Order.Status(s).label for s in allowed]
            hint = f'Hanya bisa ke: {", ".join(labels)}.'
        else:
            hint = 'Status ini adalah status akhir, tidak bisa diubah lagi.'
        raise OrderStatusTransitionError(
            f'Tidak bisa mengubah status dari "{Order.Status(order.status).label}" '
            f'ke "{Order.Status(new_status).label}". {hint}',
        )

    order.status = new_status
    order.save(update_fields=['status', 'updated_at'])
    return order


def can_transition_status(order_or_status, new_status: str) -> bool:
    """Check if a status transition is allowed without executing it.

    Accepts either an Order instance or a plain status string as the
    current status.
    """
    if isinstance(order_or_status, Order):
        current_status = order_or_status.status
    else:
        current_status = order_or_status
    allowed = ORDER_STATUS_TRANSITIONS.get(current_status, set())
    return new_status in allowed


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
            # Never trust unit_price from cart/client —
            # recalculate from DB as source of truth.
            # Variant price adjustments are re-validated via
            # MenuItemVariantOption.
            unit_price = menu_item.price
            variant_option_ids = cart_item.get('variant_option_ids') or cart_item.get(
                'variant_options', []
            )
            if variant_option_ids:
                from menus.models import MenuItemVariantOption

                try:
                    ids = [int(v) for v in variant_option_ids]
                except (TypeError, ValueError):
                    ids = []
                if ids:
                    adjustments = MenuItemVariantOption.objects.filter(
                        id__in=ids,
                        group__menu_item=menu_item,
                        group__is_active=True,
                        is_active=True,
                    ).values_list('price_adjustment', flat=True)
                    unit_price += sum(adjustments)

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
