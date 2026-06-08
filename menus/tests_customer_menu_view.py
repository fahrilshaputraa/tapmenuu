from django.test import TestCase
from django.urls import reverse

from menus.models import MenuCategory, MenuItem
from menus.views import CUSTOMER_CART_SESSION_KEY
from orders.models import Order
from payments.models import Payment
from restaurants.models import DiningTable, Restaurant


class CustomerMenuViewTests(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Kedai QR',
            slug='kedai-qr',
        )
        self.table = DiningTable.objects.create(
            restaurant=self.restaurant,
            table_number='A1',
            qr_token='qr-meja-a1',
        )
        self.category = MenuCategory.objects.create(
            restaurant=self.restaurant,
            name='Minuman',
            slug='minuman',
        )
        self.item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name='Es Teh Manis',
            slug='es-teh-manis',
            price=5000,
        )

    def test_customer_menu_url_uses_qr_token_and_renders_table_menu(self):
        response = self.client.get(
            reverse('customer_menu', kwargs={'qr_token': self.table.qr_token}),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Kedai QR')
        self.assertContains(response, 'Meja A1')
        self.assertContains(response, 'Minuman')
        self.assertContains(response, 'Es Teh Manis')
        self.assertContains(response, 'Rp 5.000')
        self.assertEqual(response.context['dining_table'], self.table)
        self.assertEqual(response.context['restaurant'], self.restaurant)
        self.assertIn(self.category, response.context['categories'])

    def test_customer_menu_returns_404_for_unknown_qr_token(self):
        response = self.client.get('/m/token-tidak-ada/')

        self.assertEqual(response.status_code, 404)

    def test_customer_menu_does_not_show_inactive_or_unavailable_items(self):
        MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name='Menu Nonaktif',
            slug='menu-nonaktif',
            price=10000,
            is_active=False,
        )
        MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name='Menu Habis',
            slug='menu-habis',
            price=12000,
            is_available=False,
        )

        response = self.client.get(
            reverse('customer_menu', kwargs={'qr_token': self.table.qr_token}),
        )

        self.assertContains(response, 'Es Teh Manis')
        self.assertNotContains(response, 'Menu Nonaktif')
        self.assertNotContains(response, 'Menu Habis')

    def test_customer_menu_renders_add_to_cart_form_for_each_item(self):
        response = self.client.get(
            reverse('customer_menu', kwargs={'qr_token': self.table.qr_token}),
        )

        self.assertContains(
            response,
            reverse(
                'customer_cart_add',
                kwargs={
                    'qr_token': self.table.qr_token,
                    'item_id': self.item.id,
                },
            ),
        )
        self.assertContains(response, 'Tambah')

    def test_customer_cart_add_stores_item_in_session_and_redirects_to_menu(self):
        response = self.client.post(
            reverse(
                'customer_cart_add',
                kwargs={
                    'qr_token': self.table.qr_token,
                    'item_id': self.item.id,
                },
            ),
            {'quantity': '2', 'note': 'tanpa gula'},
        )

        self.assertRedirects(
            response,
            reverse('customer_menu', kwargs={'qr_token': self.table.qr_token}),
        )
        cart = self.client.session[CUSTOMER_CART_SESSION_KEY]
        self.assertEqual(cart['qr_token'], self.table.qr_token)
        self.assertEqual(cart['items'][str(self.item.id)]['quantity'], 2)
        self.assertEqual(cart['items'][str(self.item.id)]['note'], 'tanpa gula')

    def test_customer_cart_add_increments_existing_item_quantity(self):
        add_url = reverse(
            'customer_cart_add',
            kwargs={
                'qr_token': self.table.qr_token,
                'item_id': self.item.id,
            },
        )

        self.client.post(add_url, {'quantity': '2'})
        self.client.post(add_url, {'quantity': '3'})

        cart = self.client.session[CUSTOMER_CART_SESSION_KEY]
        self.assertEqual(cart['items'][str(self.item.id)]['quantity'], 5)

    def test_customer_cart_add_rejects_item_from_different_restaurant(self):
        other_restaurant = Restaurant.objects.create(
            name='Kedai Lain',
            slug='kedai-lain-cart',
        )
        other_item = MenuItem.objects.create(
            restaurant=other_restaurant,
            name='Menu Beda Resto',
            slug='menu-beda-resto',
            price=10000,
        )

        response = self.client.post(
            reverse(
                'customer_cart_add',
                kwargs={
                    'qr_token': self.table.qr_token,
                    'item_id': other_item.id,
                },
            ),
            {'quantity': '1'},
        )

        self.assertEqual(response.status_code, 404)
        self.assertNotIn(CUSTOMER_CART_SESSION_KEY, self.client.session)

    def test_customer_menu_renders_cart_summary_from_session(self):
        session = self.client.session
        session[CUSTOMER_CART_SESSION_KEY] = {
            'qr_token': self.table.qr_token,
            'items': {
                str(self.item.id): {
                    'quantity': 2,
                    'note': '',
                },
            },
        }
        session.save()

        response = self.client.get(
            reverse('customer_menu', kwargs={'qr_token': self.table.qr_token}),
        )

        self.assertContains(response, 'Keranjang')
        self.assertContains(response, '2 item')
        self.assertContains(response, 'Rp 10.000')

    def test_customer_menu_renders_checkout_form_when_cart_has_items(self):
        self._put_item_in_session_cart(quantity=2)

        response = self.client.get(
            reverse('customer_menu', kwargs={'qr_token': self.table.qr_token}),
        )

        self.assertContains(
            response,
            reverse('customer_checkout', kwargs={'qr_token': self.table.qr_token}),
        )
        self.assertContains(response, 'Checkout')
        self.assertContains(response, 'Nama Customer')
        self.assertContains(response, 'Metode Pembayaran')
        self.assertContains(response, 'QRIS')

    def test_customer_checkout_creates_order_from_session_cart_and_clears_cart(self):
        self._put_item_in_session_cart(quantity=2, note='tanpa gula')

        response = self.client.post(
            reverse('customer_checkout', kwargs={'qr_token': self.table.qr_token}),
            {
                'customer_name': 'Fahril',
                'customer_note': 'antar cepat',
                'payment_method': Payment.Method.QRIS,
            },
        )

        order = Order.objects.get()
        self.assertRedirects(
            response,
            reverse(
                'customer_order_success',
                kwargs={
                    'qr_token': self.table.qr_token,
                    'order_id': order.id,
                },
            ),
        )
        self.assertEqual(order.restaurant, self.restaurant)
        self.assertEqual(order.dining_table, self.table)
        self.assertEqual(order.customer_name, 'Fahril')
        self.assertEqual(order.notes, 'antar cepat')
        self.assertEqual(order.total_amount, 10000)
        order_item = order.items.get()
        self.assertEqual(order_item.menu_item, self.item)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.notes, 'tanpa gula')
        payment = order.payments.get()
        self.assertEqual(payment.method, Payment.Method.QRIS)
        self.assertEqual(payment.amount, 10000)
        self.assertEqual(payment.provider, 'dummy')
        self.assertIn('qr_string=', payment.notes)
        self.assertNotIn(CUSTOMER_CART_SESSION_KEY, self.client.session)

    def test_customer_checkout_rejects_empty_cart_without_creating_order(self):
        response = self.client.post(
            reverse('customer_checkout', kwargs={'qr_token': self.table.qr_token}),
            {'customer_name': 'Fahril'},
        )

        self.assertRedirects(
            response,
            reverse('customer_menu', kwargs={'qr_token': self.table.qr_token}),
        )
        self.assertEqual(Order.objects.count(), 0)

    def test_customer_order_success_renders_order_summary(self):
        order = Order.objects.create(
            restaurant=self.restaurant,
            dining_table=self.table,
            code='ORD-TEST-001',
            customer_name='Fahril',
            total_amount=10000,
        )
        payment = Payment.objects.create(
            order=order,
            reference='PAY-TEST-001',
            method=Payment.Method.QRIS,
            amount=10000,
            provider='dummy',
            provider_reference='DUMMY-PAY-TEST-001',
            notes='qr_string=DUMMY-QRIS|reference=PAY-TEST-001|amount=10000',
        )

        response = self.client.get(
            reverse(
                'customer_order_success',
                kwargs={
                    'qr_token': self.table.qr_token,
                    'order_id': order.id,
                },
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pesanan berhasil dibuat')
        self.assertContains(response, 'ORD-TEST-001')
        self.assertContains(response, 'Rp 10.000')
        self.assertContains(response, payment.reference)
        self.assertContains(response, 'QRIS')
        self.assertContains(response, 'DUMMY-QRIS')

    def _put_item_in_session_cart(self, *, quantity=1, note=''):
        session = self.client.session
        session[CUSTOMER_CART_SESSION_KEY] = {
            'qr_token': self.table.qr_token,
            'items': {
                str(self.item.id): {
                    'quantity': quantity,
                    'note': note,
                },
            },
        }
        session.save()
