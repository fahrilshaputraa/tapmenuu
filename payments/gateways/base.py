from dataclasses import dataclass


@dataclass(frozen=True)
class PaymentGatewayResult:
    provider: str
    reference: str
    qr_string: str = ''
    payment_url: str = ''


class PaymentGateway:
    def create_payment(self, payment):
        raise NotImplementedError

    def verify_callback(self, payload):
        raise NotImplementedError
