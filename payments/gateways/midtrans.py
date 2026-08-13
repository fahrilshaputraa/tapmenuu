"""Midtrans payment gateway (Snap) for QRIS, Virtual Account, and E-Wallet.

Activated automatically when ``MIDTRANS_SERVER_KEY`` and ``MIDTRANS_CLIENT_KEY``
are present in settings; otherwise the ``dummy`` gateway is used.

Uses only the Python standard library (``urllib``) so no extra dependencies are
needed. The gateway is unit-tested with mocked HTTP calls.
"""

import base64
import hashlib
import json
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings

from payments.gateways.base import PaymentGateway, PaymentGatewayResult
from payments.models import Payment


class MidtransError(RuntimeError):
    """Raised when the Midtrans API returns an error or is unreachable."""


class MidtransPaymentGateway(PaymentGateway):
    provider = 'midtrans'

    # Midtrans Snap API base URLs.
    SNAP_BASE_URL_PRODUCTION = 'https://app.midtrans.com/snap/v1'
    SNAP_BASE_URL_SANDBOX = 'https://app.sandbox.midtrans.com/snap/v1'

    # Map our payment method to Midtrans Snap payment_type.
    SNAP_PAYMENT_TYPES = {
        Payment.Method.QRIS: 'qris',
        Payment.Method.BANK_TRANSFER: 'bank_transfer',
        Payment.Method.EWALLET: 'ewallet',
        Payment.Method.CASH: None,  # cash is not supported by Snap
    }

    # Map Midtrans transaction_status / fraud_status to our Payment.Status.
    STATUS_MAP = {
        'capture': Payment.Status.PAID,
        'settlement': Payment.Status.PAID,
        'paid': Payment.Status.PAID,
        'pending': Payment.Status.PENDING,
        'deny': Payment.Status.FAILED,
        'cancel': Payment.Status.EXPIRED,
        'expire': Payment.Status.EXPIRED,
        'failure': Payment.Status.FAILED,
        'refund': Payment.Status.REFUNDED,
        'partial_refund': Payment.Status.REFUNDED,
    }

    def __init__(self, server_key=None, client_key=None, is_production=None):
        self.server_key = server_key or settings.MIDTRANS_SERVER_KEY
        self.client_key = client_key or settings.MIDTRANS_CLIENT_KEY
        self.is_production = (
            is_production
            if is_production is not None
            else settings.MIDTRANS_IS_PRODUCTION
        )

    @property
    def base_url(self):
        if self.is_production:
            return self.SNAP_BASE_URL_PRODUCTION
        return self.SNAP_BASE_URL_SANDBOX

    def _is_configured(self):
        return bool(self.server_key and self.client_key)

    def create_payment(self, payment):
        """Create a Midtrans Snap transaction and return the hosted payment page."""
        if not self._is_configured():
            raise MidtransError(
                'Midtrans belum dikonfigurasi. '
                'Set MIDTRANS_SERVER_KEY dan MIDTRANS_CLIENT_KEY.',
            )

        snap_payment_type = self.SNAP_PAYMENT_TYPES.get(payment.method)
        if snap_payment_type is None:
            raise MidtransError(
                f'Metode pembayaran {payment.method} tidak didukung Midtrans.',
            )

        transaction_details = {
            'order_id': payment.reference,
            'gross_amount': payment.amount,
        }
        item_details = [
            {
                'id': payment.reference,
                'price': payment.amount,
                'quantity': 1,
                'name': f'Pesanan {payment.order.code}',
            },
        ]
        request_body = {
            'transaction_details': transaction_details,
            'item_details': item_details,
            'payment_type': snap_payment_type,
            'customer_details': {
                'first_name': payment.order.customer_name or 'Pelanggan',
            },
        }
        # For bank_transfer the payment type is selected inside Snap; we just
        # pass the top-level payment_type to let Midtrans pick a VA bank.
        if payment.method == Payment.Method.QRIS:
            request_body['qris'] = {'acquirer': 'gopay'}
        elif payment.method == Payment.Method.EWALLET:
            request_body['enabled_payments'] = ['gopay', 'shopeepay', 'ovo', 'dana']

        response_data = self._post_json(
            '/transactions',
            request_body,
        )
        token = response_data.get('token', '')
        redirect_url = response_data.get('redirect_url', '')

        return PaymentGatewayResult(
            provider=self.provider,
            reference=response_data.get(
                'order_id',
                f'MID-{uuid.uuid4().hex[:8].upper()}',
            ),
            payment_url=redirect_url or self._build_snap_url(token),
            qr_string='',
        )

    def verify_callback(self, payload):
        """Verify a Midtrans webhook notification payload.

        Returns a dict with ``provider``, ``reference``, ``status`` and the raw
        payload. Signature verification is done against the server key.
        """
        signature_key = payload.get('signature_key', '')
        order_id = payload.get('order_id', '')
        status_code = payload.get('status_code', '')
        gross_amount = payload.get('gross_amount', '')

        if not self._verify_signature(
            order_id,
            status_code,
            gross_amount,
            signature_key,
        ):
            raise MidtransError('Signature Midtrans tidak valid.')

        transaction_status = payload.get('transaction_status', '')
        fraud_status = payload.get('fraud_status', '')

        # For capture transactions, accept when fraud_status is "accept".
        if transaction_status == 'capture':
            status = (
                Payment.Status.PAID
                if fraud_status == 'accept'
                else Payment.Status.PENDING
            )
        else:
            status = self.STATUS_MAP.get(transaction_status, Payment.Status.PENDING)

        return {
            'provider': self.provider,
            'reference': order_id,
            'status': status,
            'transaction_status': transaction_status,
            'raw_payload': payload,
        }

    def _verify_signature(self, order_id, status_code, gross_amount, signature_key):
        if not self.server_key:
            return False
        raw = f'{order_id}{status_code}{gross_amount}{self.server_key}'
        expected = hashlib.sha512(raw.encode('utf-8')).hexdigest()
        return expected == signature_key

    def _build_snap_url(self, token):
        if token:
            return f'{self.base_url}/transactions/{token}'
        return ''

    def _post_json(self, path, payload):
        url = f'{self.base_url}{path}'
        body = json.dumps(payload).encode()
        credentials = base64.b64encode(
            f'{self.server_key}:'.encode(),
        ).decode('ascii')
        request = Request(
            url,
            data=body,
            method='POST',
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Basic {credentials}',
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except HTTPError as exc:
            detail = exc.read().decode('utf-8', errors='replace')
            raise MidtransError(
                f'Midtrans API error {exc.code}: {detail[:200]}',
            ) from exc
        except URLError as exc:
            raise MidtransError(f'Gagal terhubung ke Midtrans: {exc.reason}') from exc
