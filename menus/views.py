import json
import time

from django.db.models import Prefetch
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from menus.models import MenuCategory, MenuItem, MenuItemVariantOption
from orders.models import Order
from orders.services import OrderCreationError, create_order_from_cart
from payments.models import Payment
from payments.services import PaymentInitiationError, initiate_payment
from restaurants.models import DiningTable, MenuAppearanceTheme

CUSTOMER_CART_SESSION_KEY = 'customer_cart'

ORDER_STATUS_FLOW = ['new', 'paid', 'processing', 'ready', 'completed']

ORDER_STATUS_LABELS = {
    Order.Status.NEW: 'Pesanan Baru',
    Order.Status.PAID: 'Dibayar',
    Order.Status.PROCESSING: 'Diproses',
    Order.Status.READY: 'Siap Disajikan',
    Order.Status.COMPLETED: 'Selesai',
    Order.Status.CANCELLED: 'Dibatalkan',
}


def customer_menu(request, qr_token):
    dining_table = _get_active_table(qr_token)
    restaurant = dining_table.restaurant
    active_items = (
        MenuItem.objects.filter(
            restaurant=restaurant,
            is_active=True,
            is_available=True,
        )
        .prefetch_related('variant_groups__options')
        .order_by('sort_order', 'name')
    )
    categories = (
        MenuCategory.objects.filter(restaurant=restaurant, is_active=True)
        .prefetch_related(Prefetch('items', queryset=active_items))
        .order_by('sort_order', 'name')
    )
    cart_summary = _build_cart_summary(request.session, dining_table)
    appearance_theme, _ = MenuAppearanceTheme.objects.get_or_create(
        restaurant=restaurant,
    )

    return render(
        request,
        'menus/customer_menu.html',
        {
            'dining_table': dining_table,
            'restaurant': restaurant,
            'categories': categories,
            'cart_summary': cart_summary,
            'appearance_theme': appearance_theme,
            'payment_methods': _customer_payment_methods(),
        },
    )


def customer_cart(request, qr_token):
    dining_table = _get_active_table(qr_token)
    cart_summary = _build_cart_summary(request.session, dining_table)

    return render(
        request,
        'menus/customer_cart.html',
        {
            'dining_table': dining_table,
            'restaurant': dining_table.restaurant,
            'cart_summary': cart_summary,
            'payment_methods': _customer_payment_methods(),
        },
    )


def customer_cart_add(request, qr_token, item_id):
    dining_table = _get_active_table(qr_token)
    menu_item = get_object_or_404(
        MenuItem,
        id=item_id,
        restaurant=dining_table.restaurant,
        is_active=True,
        is_available=True,
    )

    quantity = _coerce_positive_quantity(request.POST.get('quantity', 1))
    note = request.POST.get('note', '').strip()
    selected_option_ids = _coerce_variant_option_ids(
        request.POST.getlist('variant_options'),
        menu_item,
    )
    cart = request.session.get(CUSTOMER_CART_SESSION_KEY)
    if not cart or cart.get('qr_token') != dining_table.qr_token:
        cart = {'qr_token': dining_table.qr_token, 'items': {}}

    item_key = _cart_line_key(menu_item.id, selected_option_ids, note)
    cart_item = cart['items'].setdefault(
        item_key,
        {
            'item_id': menu_item.id,
            'quantity': 0,
            'note': note,
            'variant_option_ids': selected_option_ids,
        },
    )
    cart_item['quantity'] += quantity
    cart_item['note'] = note
    cart_item['variant_option_ids'] = selected_option_ids

    request.session[CUSTOMER_CART_SESSION_KEY] = cart
    request.session.modified = True

    return redirect(
        reverse('customer_menu', kwargs={'qr_token': dining_table.qr_token}),
    )


def customer_cart_quantity(request, qr_token, line_key):
    dining_table = _get_active_table(qr_token)
    cart = request.session.get(CUSTOMER_CART_SESSION_KEY)

    if cart and cart.get('qr_token') == dining_table.qr_token:
        items = cart.get('items', {})
        cart_item = items.get(line_key)
        if cart_item:
            quantity = _coerce_positive_quantity(cart_item.get('quantity', 1))
            action = request.POST.get('action')
            if action == 'increment':
                cart_item['quantity'] = quantity + 1
            elif action == 'decrement':
                if quantity <= 1:
                    items.pop(line_key, None)
                else:
                    cart_item['quantity'] = quantity - 1

            _store_customer_cart(request, cart, items)

    return redirect(
        reverse('customer_cart', kwargs={'qr_token': dining_table.qr_token}),
    )


def customer_cart_remove(request, qr_token, line_key):
    dining_table = _get_active_table(qr_token)
    cart = request.session.get(CUSTOMER_CART_SESSION_KEY)

    if cart and cart.get('qr_token') == dining_table.qr_token:
        items = cart.get('items', {})
        items.pop(line_key, None)
        _store_customer_cart(request, cart, items)

    return redirect(
        reverse('customer_cart', kwargs={'qr_token': dining_table.qr_token}),
    )


def customer_checkout(request, qr_token):
    dining_table = _get_active_table(qr_token)
    cart_items = _build_order_cart_items(request.session, dining_table)
    if not cart_items:
        return redirect(
            reverse('customer_cart', kwargs={'qr_token': dining_table.qr_token}),
        )

    try:
        order = create_order_from_cart(
            table=dining_table,
            cart_items=cart_items,
            customer_name=request.POST.get('customer_name', '').strip(),
            customer_note=request.POST.get('customer_note', '').strip(),
        )
        initiate_payment(
            order=order,
            method=_get_customer_payment_method(request.POST.get('payment_method')),
        )
    except (OrderCreationError, PaymentInitiationError):
        return redirect(
            reverse('customer_menu', kwargs={'qr_token': dining_table.qr_token}),
        )

    request.session.pop(CUSTOMER_CART_SESSION_KEY, None)
    request.session.modified = True

    return redirect(
        reverse(
            'customer_order_success',
            kwargs={'qr_token': dining_table.qr_token, 'order_id': order.id},
        ),
    )


def customer_order_success(request, qr_token, order_id):
    dining_table = _get_active_table(qr_token)
    order = get_object_or_404(
        Order.objects.select_related('restaurant', 'dining_table').prefetch_related(
            'payments',
        ),
        id=order_id,
        dining_table=dining_table,
        restaurant=dining_table.restaurant,
    )
    payment = order.payments.first()

    return render(
        request,
        'menus/customer_order_success.html',
        {
            'dining_table': dining_table,
            'restaurant': dining_table.restaurant,
            'order': order,
            'payment': payment,
            'payment_details': _parse_payment_notes(payment.notes if payment else ''),
        },
    )


def customer_order_status(request, qr_token, order_id):
    """Customer-facing order status page with a live timeline."""
    dining_table = _get_active_table(qr_token)
    order = _get_customer_order(dining_table, order_id)
    payment = order.payments.first()

    current_index = _status_flow_index(order.status)
    steps = []
    for index, status_value in enumerate(ORDER_STATUS_FLOW):
        steps.append(
            {
                'value': status_value,
                'label': ORDER_STATUS_LABELS[status_value],
                'state': (
                    'done'
                    if index < current_index
                    else 'current'
                    if index == current_index
                    else 'upcoming'
                ),
            },
        )

    return render(
        request,
        'menus/customer_order_status.html',
        {
            'dining_table': dining_table,
            'restaurant': dining_table.restaurant,
            'order': order,
            'payment': payment,
            'payment_details': _parse_payment_notes(payment.notes if payment else ''),
            'steps': steps,
            'current_index': current_index,
            'status_labels': ORDER_STATUS_LABELS,
            'status_flow': ORDER_STATUS_FLOW,
        },
    )


def customer_order_stream(request, qr_token, order_id):
    """SSE endpoint that streams order status/payment updates to the customer."""
    dining_table = _get_active_table(qr_token)
    order = _get_customer_order(dining_table, order_id)

    def event_stream():
        last_status = None
        last_payment_status = None
        try:
            yield 'retry: 3000\n\n'
            for _ in range(30):  # ~60s at 2s interval
                try:
                    fresh = Order.objects.only('status', 'payment_status').get(
                        pk=order.id,
                    )
                except Order.DoesNotExist:
                    break

                if (
                    fresh.status != last_status
                    or fresh.payment_status != last_payment_status
                ):
                    data = json.dumps(_build_order_status_event(fresh))
                    yield f'event: update\ndata: {data}\n\n'
                    last_status = fresh.status
                    last_payment_status = fresh.payment_status
                else:
                    yield 'event: heartbeat\ndata: ping\n\n'

                time.sleep(2)
            yield 'event: close\ndata: done\n\n'
        except (GeneratorExit, BrokenPipeError, ConnectionResetError):
            return

    return StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream',
    )


def customer_receipt(request, qr_token, order_id):
    """Customer-facing printable 80mm thermal receipt."""
    dining_table = _get_active_table(qr_token)
    order = _get_customer_order(dining_table, order_id, with_items=True)
    payment = order.payments.first()
    subtotal = sum(item.line_total for item in order.items.all())
    theme, _ = MenuAppearanceTheme.objects.get_or_create(
        restaurant=dining_table.restaurant,
    )

    return render(
        request,
        'menus/customer_receipt.html',
        {
            'dining_table': dining_table,
            'restaurant': dining_table.restaurant,
            'order': order,
            'payment': payment,
            'subtotal': subtotal,
            'theme': theme,
            'is_staff_view': False,
        },
    )


def _build_order_status_event(order):
    """Serialize order status for an SSE update event."""
    return {
        'status': order.status,
        'status_label': ORDER_STATUS_LABELS.get(order.status, order.status),
        'payment_status': order.payment_status,
    }


def _status_flow_index(status_value):
    if status_value == Order.Status.CANCELLED:
        return -1
    try:
        return ORDER_STATUS_FLOW.index(status_value)
    except ValueError:
        return -1


def _get_customer_order(dining_table, order_id, with_items=False):
    queryset = Order.objects.select_related('restaurant', 'dining_table')
    if with_items:
        queryset = queryset.prefetch_related('items', 'payments')
    else:
        queryset = queryset.prefetch_related('payments')
    return get_object_or_404(
        queryset,
        id=order_id,
        dining_table=dining_table,
        restaurant=dining_table.restaurant,
    )


def _get_active_table(qr_token):
    return get_object_or_404(
        DiningTable.objects.select_related('restaurant'),
        qr_token=qr_token,
        is_active=True,
        restaurant__is_active=True,
    )


def _store_customer_cart(request, cart, items):
    if items:
        cart['items'] = items
        request.session[CUSTOMER_CART_SESSION_KEY] = cart
    else:
        request.session.pop(CUSTOMER_CART_SESSION_KEY, None)
    request.session.modified = True


def _coerce_positive_quantity(value):
    try:
        quantity = int(value)
    except (TypeError, ValueError):
        quantity = 1

    return max(quantity, 1)


def _build_cart_summary(session, dining_table):
    cart = session.get(CUSTOMER_CART_SESSION_KEY, {})
    if cart.get('qr_token') != dining_table.qr_token:
        return {'items': [], 'total_quantity': 0, 'total_amount': 0}

    cart_items = cart.get('items', {})
    item_ids = [
        int(cart_item.get('item_id') or line_key)
        for line_key, cart_item in cart_items.items()
    ]
    menu_items = MenuItem.objects.filter(
        id__in=item_ids,
        restaurant=dining_table.restaurant,
        is_active=True,
        is_available=True,
    ).prefetch_related('variant_groups__options')
    menu_item_by_id = {str(item.id): item for item in menu_items}

    summary_items = []
    total_quantity = 0
    total_amount = 0
    for line_key, cart_item in cart_items.items():
        item_id = str(cart_item.get('item_id') or line_key)
        menu_item = menu_item_by_id.get(item_id)
        if not menu_item:
            continue

        quantity = _coerce_positive_quantity(cart_item.get('quantity', 1))
        variant_details = _build_variant_details(
            menu_item,
            cart_item.get('variant_option_ids', []),
        )
        unit_price = menu_item.price + variant_details['price_adjustment']
        line_total = unit_price * quantity
        total_quantity += quantity
        total_amount += line_total
        summary_items.append(
            {
                'line_key': line_key,
                'menu_item': menu_item,
                'quantity': quantity,
                'note': cart_item.get('note', ''),
                'variant_labels': variant_details['labels'],
                'variant_note': variant_details['note'],
                'unit_price': unit_price,
                'line_total': line_total,
            },
        )

    return {
        'items': summary_items,
        'total_quantity': total_quantity,
        'total_amount': total_amount,
    }


def _build_order_cart_items(session, dining_table):
    summary = _build_cart_summary(session, dining_table)
    return [
        {
            'menu_item': item['menu_item'],
            'quantity': item['quantity'],
            'note': _combine_cart_notes(item['note'], item.get('variant_note', '')),
            'unit_price': item.get('unit_price', item['menu_item'].price),
        }
        for item in summary['items']
    ]


def _coerce_variant_option_ids(raw_option_ids, menu_item):
    option_ids = []
    for raw_option_id in raw_option_ids:
        try:
            option_ids.append(int(raw_option_id))
        except (TypeError, ValueError):
            continue

    if not option_ids:
        return []

    valid_option_ids = set(
        MenuItemVariantOption.objects.filter(
            id__in=option_ids,
            group__menu_item=menu_item,
            group__is_active=True,
            is_active=True,
        ).values_list('id', flat=True),
    )
    return [option_id for option_id in option_ids if option_id in valid_option_ids]


def _cart_line_key(menu_item_id, variant_option_ids, note):
    if not variant_option_ids and not note:
        return str(menu_item_id)
    variants_key = (
        '-'.join(str(option_id) for option_id in sorted(variant_option_ids)) or 'plain'
    )
    note_key = abs(hash(note)) if note else 'no-note'
    return f'{menu_item_id}:{variants_key}:{note_key}'


def _build_variant_details(menu_item, selected_option_ids):
    selected_option_ids = {int(option_id) for option_id in selected_option_ids}
    labels = []
    price_adjustment = 0

    for group in menu_item.variant_groups.all():
        group_options = [
            option
            for option in group.options.all()
            if option.is_active and option.id in selected_option_ids
        ]
        if not group.is_active or not group_options:
            continue

        option_names = []
        for option in group_options:
            option_names.append(option.name)
            price_adjustment += option.price_adjustment
        labels.append(f'{group.name}: {", ".join(option_names)}')

    return {
        'labels': labels,
        'note': '\n'.join(labels),
        'price_adjustment': price_adjustment,
    }


def _combine_cart_notes(note, variant_note):
    notes = [value for value in [variant_note, note] if value]
    return '\n'.join(notes)


def _customer_payment_methods():
    return [
        (Payment.Method.QRIS, Payment.Method.QRIS.label),
        (Payment.Method.EWALLET, Payment.Method.EWALLET.label),
        (Payment.Method.BANK_TRANSFER, Payment.Method.BANK_TRANSFER.label),
        (Payment.Method.CASH, Payment.Method.CASH.label),
    ]


def _get_customer_payment_method(value):
    valid_methods = {method for method, _label in _customer_payment_methods()}
    if value in valid_methods:
        return value
    return Payment.Method.QRIS


def _parse_payment_notes(notes):
    details = {}
    for line in notes.splitlines():
        key, separator, value = line.partition('=')
        if separator:
            details[key] = value
    return details
