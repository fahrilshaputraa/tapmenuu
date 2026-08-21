from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from restaurants.models import MenuAppearanceTheme, Restaurant


class MenuAppearanceDashboardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='owner',
            password='password12345',
            is_staff=True,
        )
        self.restaurant = Restaurant.objects.create(
            name='Kedai Tema',
            slug='kedai-tema',
        )

    def login_staff(self):
        self.client.force_login(self.user)

    def test_appearance_page_requires_staff_login(self):
        response = self.client.get(reverse('menu_appearance'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])

    def test_appearance_page_renders_form_and_phone_preview(self):
        self.login_staff()

        response = self.client.get(reverse('menu_appearance'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Appearance Menu')
        self.assertContains(response, 'Warna Tema')
        self.assertContains(response, 'Preview HP')
        self.assertContains(response, 'name="primary_color"')
        self.assertContains(response, 'name="layout_style"')
        self.assertContains(response, 'data-theme-preview')
        self.assertContains(response, 'data-preview-phone')
        self.assertContains(response, 'family=Plus+Jakarta+Sans')
        self.assertContains(response, 'family=Inter')
        self.assertContains(response, 'data-reset-theme-modal')
        self.assertContains(response, 'Ya, Reset Default')
        self.assertContains(response, 'name="reset_theme"')
        self.assertNotContains(response, 'confirm(')
        self.assertEqual(
            response.context['appearance_theme'].restaurant, self.restaurant
        )

    def test_appearance_post_saves_theme_to_database(self):
        self.login_staff()

        response = self.client.post(
            reverse('menu_appearance'),
            {
                'primary_color': '#0F766E',
                'secondary_color': '#CCFBF1',
                'accent_color': '#F97316',
                'background_color': '#FFF7ED',
                'text_color': '#111827',
                'card_color': '#FFFFFF',
                'font_family': 'Inter',
                'layout_style': MenuAppearanceTheme.LayoutStyle.COMPACT,
                'header_style': MenuAppearanceTheme.HeaderStyle.MINIMAL,
                'button_style': MenuAppearanceTheme.ButtonStyle.PILL,
                'show_category_tabs': 'on',
            },
        )

        self.assertRedirects(response, reverse('menu_appearance'))
        theme = MenuAppearanceTheme.objects.get(restaurant=self.restaurant)
        self.assertEqual(theme.primary_color, '#0F766E')
        self.assertEqual(theme.secondary_color, '#CCFBF1')
        self.assertEqual(theme.accent_color, '#F97316')
        self.assertEqual(theme.background_color, '#FFF7ED')
        self.assertEqual(theme.text_color, '#111827')
        self.assertEqual(theme.layout_style, MenuAppearanceTheme.LayoutStyle.COMPACT)
        self.assertEqual(theme.header_style, MenuAppearanceTheme.HeaderStyle.MINIMAL)
        self.assertEqual(theme.button_style, MenuAppearanceTheme.ButtonStyle.PILL)
        self.assertTrue(theme.show_category_tabs)

    def test_appearance_reset_restores_default_theme_values(self):
        self.login_staff()
        theme = MenuAppearanceTheme.objects.create(
            restaurant=self.restaurant,
            primary_color='#0F766E',
            secondary_color='#CCFBF1',
            accent_color='#F97316',
            background_color='#FFF7ED',
            text_color='#111827',
            font_family='Inter',
            layout_style=MenuAppearanceTheme.LayoutStyle.COMPACT,
            header_style=MenuAppearanceTheme.HeaderStyle.MINIMAL,
            button_style=MenuAppearanceTheme.ButtonStyle.PILL,
            show_category_tabs=False,
        )

        response = self.client.post(reverse('menu_appearance'), {'reset_theme': '1'})

        self.assertRedirects(response, reverse('menu_appearance'))
        theme.refresh_from_db()
        self.assertEqual(theme.primary_color, '#1B4332')
        self.assertEqual(theme.secondary_color, '#D8F3DC')
        self.assertEqual(theme.accent_color, '#E07A5F')
        self.assertEqual(theme.background_color, '#F7F5F2')
        self.assertEqual(theme.text_color, '#1F2933')
        self.assertEqual(theme.card_color, '#FFFFFF')
        self.assertEqual(theme.font_family, 'Plus Jakarta Sans')
        self.assertEqual(theme.layout_style, MenuAppearanceTheme.LayoutStyle.GRID)
        self.assertEqual(theme.header_style, MenuAppearanceTheme.HeaderStyle.ROUNDED)
        self.assertEqual(theme.button_style, MenuAppearanceTheme.ButtonStyle.ROUNDED)
        self.assertTrue(theme.show_category_tabs)

    def test_sidebar_contains_menu_appearance_link(self):
        self.login_staff()

        response = self.client.get(reverse('dashboard'))

        self.assertContains(response, reverse('menu_appearance'))
        self.assertContains(response, 'Appearance Menu')


class KitchenBoardTests(TestCase):
    def setUp(self):
        from accounts.models import Role, UserProfile
        from menus.models import MenuCategory, MenuItem
        from orders.models import Order
        from restaurants.models import DiningTable

        self.user = User.objects.create_user(
            username='dapur',
            password='password12345',
            is_staff=True,
        )
        UserProfile.objects.create(user=self.user, role=Role.DAPUR)
        self.restaurant = Restaurant.objects.create(
            name='Kedai Dapur',
            slug='kedai-dapur',
        )
        self.table = DiningTable.objects.create(
            restaurant=self.restaurant,
            table_number='A1',
        )
        self.category = MenuCategory.objects.create(
            restaurant=self.restaurant,
            name='Makanan',
            slug='makanan',
        )
        self.item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name='Nasi Goreng',
            slug='nasi-goreng',
            price=15000,
        )
        self.new_order = Order.objects.create(
            restaurant=self.restaurant,
            dining_table=self.table,
            code='ORD-KIT-001',
            status=Order.Status.PAID,
            payment_status=Order.PaymentStatus.PAID,
            total_amount=15000,
        )
        self.completed_order = Order.objects.create(
            restaurant=self.restaurant,
            dining_table=self.table,
            code='ORD-KIT-002',
            status=Order.Status.COMPLETED,
            total_amount=15000,
        )

    def test_dapur_can_access_kitchen_but_not_menu_management(self):
        self.client.force_login(self.user)

        kitchen_response = self.client.get(reverse('kitchen'))
        self.assertEqual(kitchen_response.status_code, 200)

        menu_response = self.client.get(reverse('management_menu'))
        self.assertEqual(menu_response.status_code, 403)

    def test_kitchen_shows_active_orders_only(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('kitchen'))

        self.assertContains(response, 'ORD-KIT-001')
        self.assertNotContains(response, 'ORD-KIT-002')

    def test_admin_receipt_requires_owner_role(self):
        kasir = User.objects.create_user(
            username='kasir',
            password='password12345',
            is_staff=True,
        )
        from accounts.models import Role, UserProfile

        UserProfile.objects.create(user=kasir, role=Role.KASIR)
        self.client.force_login(kasir)

        response = self.client.get(
            reverse('order_receipt', kwargs={'pk': self.new_order.pk}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ORD-KIT-001')
        self.assertContains(response, 'Cetak Struk')


class DashboardRevenueTests(TestCase):
    def setUp(self):
        from orders.models import Order
        from restaurants.models import DiningTable

        self.user = User.objects.create_user(
            username='owner',
            password='password12345',
            is_staff=True,
        )
        self.restaurant = Restaurant.objects.create(
            name='Kedai Revenue',
            slug='kedai-revenue',
        )
        self.table = DiningTable.objects.create(
            restaurant=self.restaurant,
            table_number='A1',
        )
        self.paid_order = Order.objects.create(
            restaurant=self.restaurant,
            dining_table=self.table,
            code='ORD-REV-001',
            total_amount=100000,
            payment_status=Order.PaymentStatus.PAID,
        )
        self.unpaid_order = Order.objects.create(
            restaurant=self.restaurant,
            dining_table=self.table,
            code='ORD-REV-002',
            total_amount=50000,
            payment_status=Order.PaymentStatus.UNPAID,
        )

    def test_dashboard_revenue_counts_only_paid_orders(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['revenue'], 100000)
        self.assertEqual(response.context['pending_payments'], 50000)
