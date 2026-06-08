from django.contrib import admin
from django.db import IntegrityError
from django.test import TestCase

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

        result = gateway.verify_callback({
            'reference': 'DUMMY-PAY-001',
            'status': 'paid',
        })

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
