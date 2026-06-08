import re

from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse


class CorePageRouteTests(TestCase):
    def test_public_and_dashboard_pages_return_success(self):
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

        for route_name in route_names:
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)

    def test_landing_auth_ctas_point_to_login_and_register_pages(self):
        response = self.client.get(reverse('landing'))
        html = response.content.decode()

        self.assertIn('href="/login/"', html)
        self.assertIn('href="/register/"', html)

    def test_dashboard_logout_link_points_to_login_page(self):
        response = self.client.get(reverse('dashboard'))
        html = response.content.decode()

        self.assertIn('href="/login/"', html)

    def test_dashboard_sidebar_uses_dynamic_django_urls(self):
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
            reverse('login'),
        ]

        for link in expected_links:
            with self.subTest(link=link):
                self.assertIn(f'href="{link}"', html)

        sidebar = html.split('data-dashboard-sidebar', 1)[1].split('</aside>', 1)[0]
        self.assertNotIn('href="javascript:void(0)"', sidebar)
        self.assertNotIn('href="#"', sidebar)

    def test_dashboard_sidebar_marks_current_route_active(self):
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

        for route_name in route_names:
            response = self.client.get(reverse(route_name))
            html = response.content.decode()
            static_paths = re.findall(r'/static/([^"\']+)', html)
            for static_path in static_paths:
                with self.subTest(route_name=route_name, static_path=static_path):
                    self.assertIsNotNone(finders.find(static_path))
