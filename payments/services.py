from uuid import uuid4

from django.db import transaction
from django.utils import timezone

from payments.gateways.dummy import DummyPaymentGateway
from payments.models import Payment


class PaymentInitiationError(ValueError):
    """Raised when a payment cannot be initiated."""


def initiate_payment(*, order, method, gateway=None):
    """Create a payment for an order and initialize it through a gateway."""
    if order.total_amount <= 0:
        raise PaymentInitiationError('Total order harus lebih dari 0.')

    if order.payments.exists():
        raise PaymentInitiationError('Order sudah memiliki payment.')

    gateway = gateway or DummyPaymentGateway()

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
