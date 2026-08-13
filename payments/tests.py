import json

from django.contrib import admin
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from orders.models import Order
from payments.gateways.base import PaymentGateway
from payments.gateways.dummy import DummyPaymentGateway
from payments.models import Payment
from payments.services import initiate_payment
from restaurants.models import DiningTable, Restaurant


class PaymentModelTests(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Kedai Payment',
            slug='kedai-payment',
        )
        self.table = DiningTable.objects.create(
            restaurant=self.restaurant,
            table_number='C3',
        )
        self.order = Order.objects.create(
            restaurant=self.restaurant,
            dining_table=self.table,
            code='PAY-ORDER-0001',
            total_amount=45000,
        )

    def test_payment_can_be_created_with_required_fields(self):
        payment = Payment.objects.create(
            order=self.order,
            reference='PAY-0001',
            method=Payment.Method.QRIS,
            amount=45000,
        )

        self.assertEqual(payment.order, self.order)
        self.assertEqual(payment.reference, 'PAY-0001')
        self.assertEqual(payment.method, Payment.Method.QRIS)
        self.assertEqual(payment.amount, 45000)
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(payment.provider, '')
        self.assertEqual(payment.provider_reference, '')
        self.assertEqual(payment.notes, '')
        self.assertIsNone(payment.paid_at)
        self.assertIsNotNone(payment.created_at)
        self.assertIsNotNone(payment.updated_at)

    def test_payment_string_representation_includes_reference_and_order_code(self):
        payment = Payment.objects.create(
            order=self.order,
            reference='PAY-0002',
            method=Payment.Method.CASH,
            amount=45000,
        )

        self.assertEqual(str(payment), 'PAY-0002 - PAY-ORDER-0001')

    def test_payment_reference_must_be_unique(self):
        Payment.objects.create(
            order=self.order,
            reference='PAY-0003',
            method=Payment.Method.CASH,
            amount=45000,
        )

        with self.assertRaises(IntegrityError):
            Payment.objects.create(
                order=self.order,
                reference='PAY-0003',
                method=Payment.Method.QRIS,
                amount=45000,
            )

    def test_mark_paid_updates_payment_and_order_status(self):
        payment = Payment.objects.create(
            order=self.order,
            reference='PAY-0004',
            method=Payment.Method.QRIS,
            amount=45000,
        )

        payment.mark_paid()
        self.order.refresh_from_db()

        self.assertEqual(payment.status, Payment.Status.PAID)
        self.assertIsNotNone(payment.paid_at)
        self.assertEqual(self.order.payment_status, Order.PaymentStatus.PAID)

    def test_payment_is_registered_in_django_admin(self):
        self.assertIn(Payment, admin.site._registry)


class PaymentGatewayTests(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Kedai Gateway',
            slug='kedai-gateway',
        )
        self.table = DiningTable.objects.create(
            restaurant=self.restaurant,
            table_number='G1',
        )
        self.order = Order.objects.create(
            restaurant=self.restaurant,
            dining_table=self.table,
            code='GATEWAY-ORDER-0001',
            total_amount=60000,
        )

    def create_payment(self, method):
        return Payment.objects.create(
            order=self.order,
            reference=f'PAY-GATEWAY-{method}',
            method=method,
            amount=60000,
        )

    def test_base_gateway_requires_create_payment_implementation(self):
        gateway = PaymentGateway()
        payment = self.create_payment(Payment.Method.CASH)

        with self.assertRaises(NotImplementedError):
            gateway.create_payment(payment)

    def test_base_gateway_requires_verify_callback_implementation(self):
        gateway = PaymentGateway()

        with self.assertRaises(NotImplementedError):
            gateway.verify_callback({'reference': 'PAY-001'})

    def test_dummy_gateway_returns_qris_payload(self):
        payment = self.create_payment(Payment.Method.QRIS)
        gateway = DummyPaymentGateway()

        result = gateway.create_payment(payment)

        self.assertEqual(result.provider, 'dummy')
        self.assertTrue(result.reference.startswith('DUMMY-'))
        self.assertIn(payment.reference, result.qr_string)
        self.assertEqual(result.payment_url, '')

    def test_dummy_gateway_returns_payment_url_for_bank_transfer(self):
        payment = self.create_payment(Payment.Method.BANK_TRANSFER)
        gateway = DummyPaymentGateway()

        result = gateway.create_payment(payment)

        self.assertEqual(result.provider, 'dummy')
        self.assertTrue(result.reference.startswith('DUMMY-'))
        self.assertEqual(result.qr_string, '')
        self.assertIn(payment.reference, result.payment_url)

    def test_dummy_gateway_returns_payment_url_for_ewallet(self):
        payment = self.create_payment(Payment.Method.EWALLET)
        gateway = DummyPaymentGateway()

        result = gateway.create_payment(payment)

        self.assertEqual(result.provider, 'dummy')
        self.assertTrue(result.reference.startswith('DUMMY-'))
        self.assertEqual(result.qr_string, '')
        self.assertIn(payment.reference, result.payment_url)

    def test_dummy_gateway_verify_callback_returns_normalized_payload(self):
        gateway = DummyPaymentGateway()

        result = gateway.verify_callback(
            {
                'reference': 'DUMMY-PAY-001',
                'status': 'paid',
            }
        )

        self.assertEqual(result['reference'], 'DUMMY-PAY-001')
        self.assertEqual(result['status'], Payment.Status.PAID)
        self.assertEqual(result['provider'], 'dummy')


class InitiatePaymentServiceTests(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Kedai Payment Service',
            slug='kedai-payment-service',
        )
        self.table = DiningTable.objects.create(
            restaurant=self.restaurant,
            table_number='P1',
        )
        self.order = Order.objects.create(
            restaurant=self.restaurant,
            dining_table=self.table,
            code='PAY-SERVICE-ORDER-0001',
            total_amount=75000,
        )

    def test_initiate_payment_creates_payment_with_order_amount(self):
        payment = initiate_payment(order=self.order, method=Payment.Method.QRIS)

        self.assertEqual(payment.order, self.order)
        self.assertTrue(payment.reference.startswith('PAY-'))
        self.assertEqual(payment.method, Payment.Method.QRIS)
        self.assertEqual(payment.amount, 75000)
        self.assertEqual(payment.status, Payment.Status.PENDING)

    def test_initiate_payment_saves_dummy_gateway_result_for_qris(self):
        payment = initiate_payment(order=self.order, method=Payment.Method.QRIS)

        self.assertEqual(payment.provider, 'dummy')
        self.assertTrue(payment.provider_reference.startswith('DUMMY-'))
        self.assertIn('qr_string=', payment.notes)
        self.assertIn(payment.reference, payment.notes)

    def test_initiate_payment_saves_dummy_gateway_result_for_ewallet(self):
        payment = initiate_payment(order=self.order, method=Payment.Method.EWALLET)

        self.assertEqual(payment.provider, 'dummy')
        self.assertTrue(payment.provider_reference.startswith('DUMMY-'))
        self.assertIn('payment_url=', payment.notes)
        self.assertIn(payment.reference, payment.notes)

    def test_initiate_payment_rejects_second_payment_for_same_order(self):
        initiate_payment(order=self.order, method=Payment.Method.QRIS)

        with self.assertRaisesMessage(ValueError, 'Order sudah memiliki payment.'):
            initiate_payment(order=self.order, method=Payment.Method.EWALLET)

    def test_initiate_payment_rejects_zero_amount_order(self):
        self.order.total_amount = 0
        self.order.save(update_fields=['total_amount'])

        with self.assertRaisesMessage(ValueError, 'Total order harus lebih dari 0.'):
            initiate_payment(order=self.order, method=Payment.Method.QRIS)

    def test_initiate_payment_accepts_custom_gateway(self):
        class FixedGateway(PaymentGateway):
            def create_payment(self, payment):
                from payments.gateways.base import PaymentGatewayResult

                return PaymentGatewayResult(
                    provider='fixed',
                    reference='FIXED-REF-001',
                    payment_url='https://fixed.test/pay',
                )

            def verify_callback(self, payload):
                return payload

        payment = initiate_payment(
            order=self.order,
            method=Payment.Method.BANK_TRANSFER,
            gateway=FixedGateway(),
        )

        self.assertEqual(payment.provider, 'fixed')
        self.assertEqual(payment.provider_reference, 'FIXED-REF-001')
        self.assertIn('https://fixed.test/pay', payment.notes)


class MidtransGatewayTests(TestCase):
    def setUp(self):
        from payments.gateways.midtrans import MidtransPaymentGateway

        self.restaurant = Restaurant.objects.create(
            name='Kedai Midtrans',
            slug='kedai-midtrans',
        )
        self.table = DiningTable.objects.create(
            restaurant=self.restaurant,
            table_number='D1',
        )
        self.order = Order.objects.create(
            restaurant=self.restaurant,
            dining_table=self.table,
            code='MID-ORDER-001',
            customer_name='Budi',
            total_amount=50000,
        )
        self.gateway = MidtransPaymentGateway(
            server_key='SB-Mid-server-abc123',
            client_key='SB-Mid-client-xyz789',
            is_production=False,
        )

    def _mock_urlopen(self, response_body, status_code=200):
        from unittest import mock
        from urllib.error import HTTPError

        class FakeResponse:
            def __init__(self, body):
                self._body = body

            def read(self):
                return self._body.encode('utf-8')

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        if status_code >= 400:
            def raise_error(*args, **kwargs):
                raise HTTPError(
                    'https://app.sandbox.midtrans.com/snap/v1/transactions',
                    status_code,
                    'Error',
                    {},
                    FakeResponse(response_body),
                )
            return mock.patch('payments.gateways.midtrans.urlopen', raise_error)

        return mock.patch(
            'payments.gateways.midtrans.urlopen',
            return_value=FakeResponse(response_body),
        )

    def test_create_payment_qris_returns_snap_redirect_url(self):
        with self._mock_urlopen(
            json.dumps({'token': 'snap-token-1', 'redirect_url': 'https://snap.test/pay/1'})
        ):
            result = self.gateway.create_payment(self._make_payment())

        self.assertEqual(result.provider, 'midtrans')
        self.assertEqual(result.payment_url, 'https://snap.test/pay/1')

    def test_verify_callback_valid_signature_marks_paid(self):
        import hashlib

        order_id = 'MID-ORDER-001'
        status_code = '200'
        gross_amount = '50000.00'
        signature_key = hashlib.sha512(
            f'{order_id}{status_code}{gross_amount}SB-Mid-server-abc123'.encode()
        ).hexdigest()
        payload = {
            'order_id': order_id,
            'status_code': status_code,
            'gross_amount': gross_amount,
            'transaction_status': 'settlement',
            'signature_key': signature_key,
        }

        verified = self.gateway.verify_callback(payload)

        self.assertEqual(verified['provider'], 'midtrans')
        self.assertEqual(verified['status'], Payment.Status.PAID)
        self.assertEqual(verified['reference'], order_id)

    def test_verify_callback_invalid_signature_raises(self):
        payload = {
            'order_id': 'MID-ORDER-001',
            'status_code': '200',
            'gross_amount': '50000.00',
            'transaction_status': 'settlement',
            'signature_key': 'wrong-signature',
        }

        from payments.gateways.midtrans import MidtransError

        with self.assertRaises(MidtransError):
            self.gateway.verify_callback(payload)

    def test_verify_callback_capture_with_accept_fraud_is_paid(self):
        import hashlib

        order_id = 'MID-ORDER-001'
        status_code = '200'
        gross_amount = '50000.00'
        signature_key = hashlib.sha512(
            f'{order_id}{status_code}{gross_amount}SB-Mid-server-abc123'.encode()
        ).hexdigest()
        payload = {
            'order_id': order_id,
            'status_code': status_code,
            'gross_amount': gross_amount,
            'transaction_status': 'capture',
            'fraud_status': 'accept',
            'signature_key': signature_key,
        }

        verified = self.gateway.verify_callback(payload)

        self.assertEqual(verified['status'], Payment.Status.PAID)

    def test_webhook_midtrans_notification_marks_order_paid(self):
        import hashlib

        payment = Payment.objects.create(
            order=self.order,
            reference='PAY-MID-WEBHOOK-001',
            method=Payment.Method.QRIS,
            amount=50000,
        )
        order_id = payment.reference
        status_code = '200'
        gross_amount = '50000.00'
        signature_key = hashlib.sha512(
            f'{order_id}{status_code}{gross_amount}SB-Mid-server-abc123'.encode()
        ).hexdigest()
        payload = {
            'order_id': order_id,
            'status_code': status_code,
            'gross_amount': gross_amount,
            'transaction_status': 'settlement',
            'signature_key': signature_key,
        }

        from payments.gateways.midtrans import MidtransPaymentGateway

        with self.settings(
            MIDTRANS_SERVER_KEY='SB-Mid-server-abc123',
            MIDTRANS_CLIENT_KEY='SB-Mid-client-xyz789',
        ):
            gateway = MidtransPaymentGateway()
            self.assertEqual(gateway.server_key, 'SB-Mid-server-abc123')
            response = self.client.post(
                reverse('payment_webhook'),
                data=json.dumps(payload),
                content_type='application/json',
            )

        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.PAID)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, Order.PaymentStatus.PAID)

    def test_gateway_selection_uses_dummy_without_keys(self):
        from payments.services import get_payment_gateway

        with self.settings(MIDTRANS_SERVER_KEY='', MIDTRANS_CLIENT_KEY=''):
            gateway = get_payment_gateway()
            self.assertEqual(gateway.provider, 'dummy')

    def test_gateway_selection_uses_midtrans_with_keys(self):
        from payments.services import get_payment_gateway

        with self.settings(
            MIDTRANS_SERVER_KEY='SB-Mid-server-abc123',
            MIDTRANS_CLIENT_KEY='SB-Mid-client-xyz789',
        ):
            gateway = get_payment_gateway()
            self.assertEqual(gateway.provider, 'midtrans')

    def _make_payment(self):
        from payments.gateways.base import PaymentGatewayResult  # noqa: F401

        return Payment(
            order=self.order,
            reference='PAY-MID-0001',
            method=Payment.Method.QRIS,
            amount=50000,
        )
