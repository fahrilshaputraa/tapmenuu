from uuid import uuid4

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from payments.gateways.dummy import DummyPaymentGateway
from payments.models import Payment


class PaymentInitiationError(ValueError):
    """Raised when a payment cannot be initiated."""


def get_payment_gateway(*, restaurant=None, order=None):
    """Return the active payment gateway.

    Resolution order (multi-tenant aware):
    1. Per-restaurant RestaurantPaymentConfig (is_active + keys) when restaurant/order given.
    2. Global settings MIDTRANS_SERVER_KEY / MIDTRANS_CLIENT_KEY (legacy / single-tenant fallback).
    3. Dummy gateway.

    Keep ``get_payment_gateway()`` with no args for backwards-compat (global fallback).
    """
    # Per-restaurant config — highest priority
    target_restaurant = restaurant
    if order is not None and target_restaurant is None:
        target_restaurant = getattr(order, 'restaurant', None)

    if target_restaurant is not None:
        try:
            # Lazy import to avoid circular
            from payments.models import RestaurantPaymentConfig

            # Use cached relation if already fetched, else query
            config = getattr(target_restaurant, 'payment_config', None)
            if config is None and hasattr(target_restaurant, 'id'):
                try:
                    config = RestaurantPaymentConfig.objects.get(
                        restaurant=target_restaurant
                    )
                except RestaurantPaymentConfig.DoesNotExist:
                    config = None
            if config and config.is_active:
                if (
                    config.gateway == config.Gateway.MIDTRANS
                    and config.is_midtrans_configured
                ):
                    from payments.gateways.midtrans import MidtransPaymentGateway

                    return MidtransPaymentGateway(
                        server_key=config.midtrans_server_key,
                        client_key=config.midtrans_client_key,
                        is_production=config.midtrans_is_production,
                    )
                if config.gateway == config.Gateway.DUMMY:
                    return DummyPaymentGateway()
                # Active config but not fully set up -> fall through to global check
                # so missing keys don't silently stay dummy if global keys exist.
        except Exception:
            pass

    # Global fallback (legacy .env)
    if settings.MIDTRANS_SERVER_KEY and settings.MIDTRANS_CLIENT_KEY:
        from payments.gateways.midtrans import MidtransPaymentGateway

        return MidtransPaymentGateway()
    return DummyPaymentGateway()


def get_payment_gateway_for_order(order):
    """Convenience helper: gateway scoped to the order's restaurant."""
    return get_payment_gateway(order=order)


def initiate_payment(*, order, method, gateway=None):
    """Create a payment for an order and initialize it through a gateway."""
    if order.total_amount <= 0:
        raise PaymentInitiationError('Total order harus lebih dari 0.')

    if order.payments.exists():
        raise PaymentInitiationError('Order sudah memiliki payment.')

    # Cash is an offline payment: create it directly without a gateway so it
    # works even when a real gateway (e.g. Midtrans) is configured.
    if method == Payment.Method.CASH:
        with transaction.atomic():
            payment = Payment.objects.create(
                order=order,
                reference=_generate_payment_reference(),
                method=method,
                amount=order.total_amount,
                provider='offline',
            )
        return payment

    gateway = gateway or get_payment_gateway(order=order)

    with transaction.atomic():
        payment = Payment.objects.create(
            order=order,
            reference=_generate_payment_reference(),
            method=method,
            amount=order.total_amount,
        )

        gateway_result = gateway.create_payment(payment)
        payment.provider = gateway_result.provider
        payment.provider_reference = gateway_result.reference
        payment.notes = _serialize_gateway_result(gateway_result)
        payment.save(
            update_fields=['provider', 'provider_reference', 'notes', 'updated_at'],
        )

        return payment


def _generate_payment_reference():
    today = timezone.localdate().strftime('%Y%m%d')
    suffix = uuid4().hex[:8].upper()
    return f'PAY-{today}-{suffix}'


def _serialize_gateway_result(gateway_result):
    notes = []
    if gateway_result.qr_string:
        notes.append(f'qr_string={gateway_result.qr_string}')
    if gateway_result.payment_url:
        notes.append(f'payment_url={gateway_result.payment_url}')
    return '\n'.join(notes)
