from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from menus.models import MenuCategory, MenuItem
from orders.models import Order
from payments.models import Payment
from restaurants.models import DiningTable, Restaurant


class DashboardEndToEndTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='password12345',
            is_staff=True,
        )
        from accounts.models import Role, UserProfile

        UserProfile.objects.create(user=self.user, role=Role.OWNER)
        self.restaurant = Restaurant.objects.create(
            name='Warung Test',
            slug='warung-test',
            phone='0812',
            address='Bandung',
        )
        self.table = DiningTable.objects.create(
            restaurant=self.restaurant,
            table_number='A1',
            capacity=4,
        )
        self.category = MenuCategory.objects.create(
            restaurant=self.restaurant,
            name='Makanan',
            slug='makanan',
        )
        self.item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name='Ayam Geprek',
            slug='ayam-geprek',
            price=15000,
        )
        self.order = Order.objects.create(
            restaurant=self.restaurant,
            dining_table=self.table,
            code='ORD-TEST-001',
            customer_name='Fahril',
            total_amount=15000,
        )
        self.payment = Payment.objects.create(
            order=self.order,
            reference='PAY-TEST-001',
            method=Payment.Method.QRIS,
            amount=15000,
        )

    def test_dashboard_requires_authenticated_staff(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

        non_staff = User.objects.create_user(
            username='customer',
            password='password12345',
        )
        self.client.force_login(non_staff)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_reports_and_seed_command_are_available(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Laporan')

    def test_dashboard_pages_show_model_data_without_source_labels_or_design_dummy_data(self):
        self.client.force_login(self.user)

        dashboard = self.client.get(reverse('dashboard')).content.decode()
        self.assertIn(self.order.code, dashboard)
        self.assertNotIn('DATA REAL', dashboard)
        self.assertNotIn('DATA DUMMY', dashboard)
        self.assertNotIn('Demo Seed', dashboard)
        self.assertNotIn('ORDER CUSTOMER', dashboard)
        self.assertNotIn('Order #TM-2048', dashboard)
        self.assertNotIn('Rp 2.072.000', dashboard)

        orders = self.client.get(reverse('orders')).content.decode()
        self.assertIn(self.order.code, orders)
        self.assertNotIn('DATA REAL', orders)
        self.assertNotIn('DATA DUMMY', orders)
        self.assertNotIn('Demo Seed', orders)
        self.assertNotIn('ORD-1024', orders)
        self.assertNotIn('orders will be injected', orders.lower())

        reports = self.client.get(reverse('reports')).content.decode()
        self.assertIn(self.order.code, reports)
        self.assertNotIn('DATA REAL', reports)
        self.assertNotIn('ORD-0094', reports)
        self.assertNotIn('DATA DUMMY', reports)
        self.assertNotIn('Demo Seed', reports)

    def test_login_logout_and_register_flow(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'owner', 'password': 'password12345'},
        )
        self.assertRedirects(response, reverse('dashboard'))

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

        response = self.client.post(
            reverse('register'),
            {
                'username': 'newowner',
                'email': 'newowner@example.com',
                'password1': 'strong-password-123',
                'password2': 'strong-password-123',
                'restaurant_name': 'Toko Baru',
            },
        )
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(
            User.objects.filter(username='newowner', is_staff=True).exists(),
        )
        self.assertTrue(Restaurant.objects.filter(slug='toko-baru').exists())

    def test_dashboard_crud_pages_are_end_to_end(self):
        self.client.force_login(self.user)
        pages = [
            'dashboard',
            'store',
            'tables',
            'management_menu',
            'orders',
            'reports',
            'employee',
        ]
        for name in pages:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse('store'),
            {
                'name': 'Warung Update',
                'slug': 'warung-update',
                'description': 'Updated',
                'address': 'Jakarta',
                'phone': '0813',
                'is_active': 'on',
            },
        )
        self.assertRedirects(response, reverse('store'))
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.name, 'Warung Update')

        response = self.client.post(
            reverse('table_create'),
            {
                'restaurant': self.restaurant.id,
                'table_number': 'B2',
                'capacity': 2,
                'is_active': 'on',
            },
        )
        self.assertRedirects(response, reverse('tables'))
        self.assertTrue(DiningTable.objects.filter(table_number='B2').exists())

        response = self.client.post(
            reverse('category_create'),
            {
                'restaurant': self.restaurant.id,
                'name': 'Minuman',
                'sort_order': 2,
                'is_active': 'on',
            },
        )
        self.assertRedirects(response, reverse('category_management'))
        category = MenuCategory.objects.get(slug='minuman')

        response = self.client.post(
            reverse('menu_item_create'),
            {
                'restaurant': self.restaurant.id,
                'category': category.id,
                'name': 'Es Teh',
                'description': 'Segar',
                'price': 5000,
                'discount': 0,
                'tax': 10,
                'stock': 0,
                'sort_order': 3,
                'is_available': 'on',
                'is_active': 'on',
            },
        )
        self.assertRedirects(response, reverse('management_menu'))
        self.assertTrue(MenuItem.objects.filter(slug='es-teh').exists())

        response = self.client.post(
            reverse('order_update_status', kwargs={'pk': self.order.pk}),
            {'status': Order.Status.PROCESSING},
        )
        self.assertRedirects(
            response,
            reverse('order_detail', kwargs={'pk': self.order.pk}),
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.PROCESSING)

        response = self.client.post(
            reverse('order_update_status', kwargs={'pk': self.order.pk}),
            {'status': Order.Status.READY},
        )
        self.assertRedirects(
            response,
            reverse('order_detail', kwargs={'pk': self.order.pk}),
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.READY)

    def test_menu_and_table_pages_expose_real_crud_controls(self):
        self.client.force_login(self.user)

        menus = self.client.get(reverse('management_menu'))
        self.assertEqual(menus.status_code, 200)
        self.assertContains(menus, reverse('menu_item_create'))
        self.assertContains(menus, reverse('menu_item_update', kwargs={'pk': self.item.pk}))
        self.assertContains(menus, reverse('menu_item_delete', kwargs={'pk': self.item.pk}))
        self.assertContains(menus, self.item.name)
        self.assertContains(menus, 'Tambah Menu')
        self.assertContains(menus, 'Edit')
        self.assertContains(menus, 'Hapus')
        self.assertNotContains(menus, 'Nasi Goreng Spesial')
        self.assertNotContains(menus, 'Items will be injected by JS')

        tables = self.client.get(reverse('tables'))
        self.assertEqual(tables.status_code, 200)
        self.assertContains(tables, reverse('table_create'))
        self.assertContains(tables, 'Tambah Meja Baru')
        self.assertContains(tables, 'Simpan Meja')
        self.assertContains(tables, 'name="table_number"')
        self.assertContains(tables, 'table-modal')
        self.assertContains(tables, 'openTableModal')
        self.assertContains(tables, 'openEditTableModal')
        self.assertContains(tables, reverse('table_delete', kwargs={'pk': self.table.pk}))
        self.assertContains(tables, reverse('customer_menu', kwargs={'qr_token': self.table.qr_token}))
        self.assertContains(tables, self.table.qr_token)
        self.assertContains(tables, 'Print QR')
        self.assertContains(tables, 'Salin Link')
        self.assertContains(tables, 'api.qrserver.com')
        self.assertContains(tables, 'data-table-number')
        self.assertContains(tables, 'data-is-active')
        self.assertContains(tables, 'data-capacity')
        self.assertNotContains(tables, 'QR siap dibagikan')
        self.assertNotContains(tables, 'Prototype tampilan meja')
        self.assertNotContains(tables, 'Meja 8')

    def test_dummy_payment_success_and_webhook(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse(
                'payment_dummy_success',
                kwargs={'reference': self.payment.reference},
            ),
        )
        self.assertRedirects(
            response,
            reverse('order_detail', kwargs={'pk': self.order.pk}),
        )
        self.payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.Status.PAID)
        self.assertEqual(self.order.payment_status, Order.PaymentStatus.PAID)

        response = self.client.post(
            reverse('payment_webhook'),
            data={'reference': self.payment.reference, 'status': 'paid'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['status'], 'ignored')

        with self.settings(PAYMENT_WEBHOOK_SECRET='test-webhook-secret'):
            response = self.client.post(
                reverse('payment_webhook'),
                data={'reference': self.payment.reference, 'status': 'paid'},
                content_type='application/json',
                HTTP_AUTHORIZATION='Bearer test-webhook-secret',
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
