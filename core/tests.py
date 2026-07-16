import re
from urllib.parse import urlsplit

from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from restaurants.models import DiningTable, Restaurant


class CorePageRouteTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='owner',
            password='password12345',
            is_staff=True,
        )

    def login_staff(self):
        self.client.force_login(self.staff_user)

    def test_public_and_dashboard_pages_return_success(self):
        public_route_names = [
            'landing',
            'login',
            'register',
            'book_menu',
        ]
        dashboard_route_names = [
            'dashboard',
            'management_menu',
            'store',
            'orders',
            'employee',
            'reports',
            'tables',
        ]

        for route_name in public_route_names:
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)

        self.login_staff()
        for route_name in dashboard_route_names:
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)

    def test_menu_route_redirects_to_qr_table_menu_when_table_exists(self):
        restaurant = Restaurant.objects.create(
            name='Kedai Digital',
            slug='kedai-digital',
            is_active=True,
        )
        dining_table = DiningTable.objects.create(
            restaurant=restaurant,
            table_number='A1',
        )

        response = self.client.get(reverse('book_menu'))

        self.assertRedirects(
            response,
            reverse('customer_menu', kwargs={'qr_token': dining_table.qr_token}),
            fetch_redirect_response=False,
        )

    def test_landing_auth_ctas_point_to_login_and_register_pages(self):
        response = self.client.get(reverse('landing'))
        html = response.content.decode()

        self.assertIn('href="/login/"', html)
        self.assertIn('href="/register/"', html)

    def test_dashboard_logout_link_points_to_logout_route(self):
        self.login_staff()
        response = self.client.get(reverse('dashboard'))
        html = response.content.decode()

        self.assertIn('href="/logout/"', html)

    def test_dashboard_sidebar_uses_dynamic_django_urls(self):
        self.login_staff()
        response = self.client.get(reverse('dashboard'))
        html = response.content.decode()

        expected_links = [
            reverse('dashboard'),
            reverse('orders'),
            reverse('tables'),
            reverse('management_menu'),
            reverse('reports'),
            reverse('store'),
            reverse('employee'),
            reverse('book_menu'),
            reverse('logout'),
        ]

        for link in expected_links:
            with self.subTest(link=link):
                self.assertIn(f'href="{link}"', html)

        sidebar = html.split('data-dashboard-sidebar', 1)[1].split('</aside>', 1)[0]
        self.assertNotIn('href="javascript:void(0)"', sidebar)
        self.assertNotIn('href="#"', sidebar)

    def test_dashboard_sidebar_marks_current_route_active(self):
        self.login_staff()
        route_names = [
            'dashboard',
            'orders',
            'tables',
            'management_menu',
            'reports',
            'store',
            'employee',
        ]

        for route_name in route_names:
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                html = response.content.decode()
                self.assertIn(f'aria-current="{route_name}"', html)

    def test_primary_auth_and_dashboard_actions_use_real_links(self):
        response = self.client.get(reverse('landing'))
        landing_html = response.content.decode()
        self.assertIn('href="/register/"', landing_html)
        self.assertNotRegex(
            landing_html,
            r'<button[^>]*>\s*<span>Coba Gratis Sekarang</span>',
        )

        response = self.client.get(reverse('login'))
        login_html = response.content.decode()
        self.assertIn('href="/register/"', login_html)
        self.assertNotRegex(
            login_html,
            r'<button[^>]*>\s*.*Daftar Toko Baru.*</button>',
        )

        self.login_staff()
        response = self.client.get(reverse('dashboard'))
        dashboard_html = response.content.decode()
        self.assertIn('href="/dashboard/menus/"', dashboard_html)
        self.assertIn('href="/dashboard/reports/"', dashboard_html)
        self.assertNotIn(
            '>Tambah Menu</span>\n                        </button>',
            dashboard_html,
        )

    def test_page_static_assets_are_discoverable(self):
        route_names = [
            'landing',
            'login',
            'register',
            'dashboard',
            'management_menu',
            'store',
            'orders',
            'employee',
            'reports',
            'tables',
            'book_menu',
        ]

        self.login_staff()
        for route_name in route_names:
            response = self.client.get(reverse(route_name))
            html = response.content.decode()
            static_paths = re.findall(r'/static/([^"\']+)', html)
            for static_path in static_paths:
                static_path_without_query = urlsplit(static_path).path
                with self.subTest(
                    route_name=route_name,
                    static_path=static_path_without_query,
                ):
                    self.assertIsNotNone(finders.find(static_path_without_query))
