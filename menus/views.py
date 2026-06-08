from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from menus.models import MenuCategory, MenuItem
from orders.models import Order
from orders.services import OrderCreationError, create_order_from_cart
from payments.models import Payment
from payments.services import PaymentInitiationError, initiate_payment
from restaurants.models import DiningTable

CUSTOMER_CART_SESSION_KEY = 'customer_cart'


def customer_menu(request, qr_token):
    dining_table = _get_active_table(qr_token)
    restaurant = dining_table.restaurant
    active_items = MenuItem.objects.filter(
        restaurant=restaurant,
        is_active=True,
        is_available=True,
    ).order_by('sort_order', 'name')
    categories = (
        MenuCategory.objects.filter(restaurant=restaurant, is_active=True)
        .prefetch_related(Prefetch('items', queryset=active_items))
        .order_by('sort_order', 'name')
    )
    cart_summary = _build_cart_summary(request.session, dining_table)

    return render(
        request,
        'menus/customer_menu.html',
        {
            'dining_table': dining_table,
            'restaurant': restaurant,
            'categories': categories,
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
    cart = request.session.get(CUSTOMER_CART_SESSION_KEY)
    if not cart or cart.get('qr_token') != dining_table.qr_token:
        cart = {'qr_token': dining_table.qr_token, 'items': {}}

    item_key = str(menu_item.id)
    cart_item = cart['items'].setdefault(
        item_key,
        {
            'quantity': 0,
            'note': '',
        },
    )
    cart_item['quantity'] += quantity
    if note:
        cart_item['note'] = note

    request.session[CUSTOMER_CART_SESSION_KEY] = cart
    request.session.modified = True

    return redirect(
        reverse('customer_menu', kwargs={'qr_token': dining_table.qr_token}),
    )


def customer_checkout(request, qr_token):
    dining_table = _get_active_table(qr_token)
    cart_items = _build_order_cart_items(request.session, dining_table)
    if not cart_items:
        return redirect(
            reverse('customer_menu', kwargs={'qr_token': dining_table.qr_token}),
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


def _get_active_table(qr_token):
    return get_object_or_404(
        DiningTable.objects.select_related('restaurant'),
        qr_token=qr_token,
        is_active=True,
        restaurant__is_active=True,
    )


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
    item_ids = [int(item_id) for item_id in cart_items]
    menu_items = MenuItem.objects.filter(
        id__in=item_ids,
        restaurant=dining_table.restaurant,
        is_active=True,
        is_available=True,
    )
    menu_item_by_id = {str(item.id): item for item in menu_items}

    summary_items = []
    total_quantity = 0
    total_amount = 0
    for item_id, cart_item in cart_items.items():
        menu_item = menu_item_by_id.get(item_id)
        if not menu_item:
            continue

        quantity = _coerce_positive_quantity(cart_item.get('quantity', 1))
        line_total = menu_item.price * quantity
        total_quantity += quantity
        total_amount += line_total
        summary_items.append(
            {
                'menu_item': menu_item,
                'quantity': quantity,
                'note': cart_item.get('note', ''),
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
            'note': item['note'],
        }
        for item in summary['items']
    ]


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
