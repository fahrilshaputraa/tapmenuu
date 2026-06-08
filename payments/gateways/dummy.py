from uuid import uuid4

from payments.gateways.base import PaymentGateway, PaymentGatewayResult
from payments.models import Payment


class DummyPaymentGateway(PaymentGateway):
    provider = 'dummy'

    def create_payment(self, payment):
        reference = self._build_reference(payment)

        if payment.method == Payment.Method.QRIS:
            return PaymentGatewayResult(
                provider=self.provider,
                reference=reference,
                qr_string=f'DUMMY-QRIS|reference={payment.reference}|amount={payment.amount}',
            )

        return PaymentGatewayResult(
            provider=self.provider,
            reference=reference,
            payment_url=f'https://dummy-payment.local/pay/{payment.reference}',
        )

    def verify_callback(self, payload):
        return {
            'provider': self.provider,
            'reference': payload.get('reference', ''),
            'status': payload.get('status', Payment.Status.PENDING),
            'raw_payload': payload,
        }

    def _build_reference(self, payment):
        suffix = uuid4().hex[:8].upper()
        return f'DUMMY-{payment.reference}-{suffix}'
