from uuid import uuid4

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from payments.gateways.dummy import DummyPaymentGateway
from payments.models import Payment


class PaymentInitiationError(ValueError):
    """Raised when a payment cannot be initiated."""


def get_payment_gateway():
    """Return the active payment gateway.

    Midtrans is used when its server/client keys are configured; otherwise the
    dummy gateway is used for development (no network, no keys).
    """
    if settings.MIDTRANS_SERVER_KEY and settings.MIDTRANS_CLIENT_KEY:
        from payments.gateways.midtrans import MidtransPaymentGateway

        return MidtransPaymentGateway()
    return DummyPaymentGateway()


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

    gateway = gateway or get_payment_gateway()

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
