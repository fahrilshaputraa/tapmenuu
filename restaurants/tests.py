from django.contrib import admin
from django.db import IntegrityError
from django.test import TestCase

from restaurants.models import DiningTable, MenuAppearanceTheme, Restaurant


class RestaurantModelTests(TestCase):
    def test_restaurant_can_be_created_with_required_fields(self):
        restaurant = Restaurant.objects.create(
            name='Kopi Nusantara',
            slug='kopi-nusantara',
        )

        self.assertEqual(restaurant.name, 'Kopi Nusantara')
        self.assertEqual(restaurant.slug, 'kopi-nusantara')
        self.assertEqual(restaurant.description, '')
        self.assertEqual(restaurant.address, '')
        self.assertEqual(restaurant.phone, '')
        self.assertTrue(restaurant.is_active)
        self.assertIsNotNone(restaurant.created_at)
        self.assertIsNotNone(restaurant.updated_at)

    def test_restaurant_string_representation_returns_name(self):
        restaurant = Restaurant.objects.create(
            name='Warung Digital',
            slug='warung-digital',
        )

        self.assertEqual(str(restaurant), 'Warung Digital')

    def test_restaurant_slug_must_be_unique(self):
        Restaurant.objects.create(name='Resto Pertama', slug='resto-sama')

        with self.assertRaises(IntegrityError):
            Restaurant.objects.create(name='Resto Kedua', slug='resto-sama')

    def test_restaurant_is_registered_in_django_admin(self):
        self.assertIn(Restaurant, admin.site._registry)


class DiningTableModelTests(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Kedai Digital',
            slug='kedai-digital',
        )

    def test_dining_table_can_be_created_with_required_fields(self):
        dining_table = DiningTable.objects.create(
            restaurant=self.restaurant,
            table_number='A1',
        )

        self.assertEqual(dining_table.restaurant, self.restaurant)
        self.assertEqual(dining_table.table_number, 'A1')
        self.assertEqual(dining_table.capacity, 2)
        self.assertTrue(dining_table.qr_token)
        self.assertTrue(dining_table.is_active)
        self.assertIsNotNone(dining_table.created_at)
        self.assertIsNotNone(dining_table.updated_at)

    def test_dining_table_string_representation_includes_restaurant_and_table_number(
        self,
    ):
        dining_table = DiningTable.objects.create(
            restaurant=self.restaurant,
            table_number='B2',
        )

        self.assertEqual(str(dining_table), 'Kedai Digital - Meja B2')

    def test_table_number_must_be_unique_per_restaurant(self):
        DiningTable.objects.create(restaurant=self.restaurant, table_number='A1')

        with self.assertRaises(IntegrityError):
            DiningTable.objects.create(restaurant=self.restaurant, table_number='A1')

    def test_same_table_number_is_allowed_for_different_restaurants(self):
        other_restaurant = Restaurant.objects.create(
            name='Resto Cabang',
            slug='resto-cabang',
        )
        DiningTable.objects.create(restaurant=self.restaurant, table_number='A1')
        dining_table = DiningTable.objects.create(
            restaurant=other_restaurant,
            table_number='A1',
        )

        self.assertEqual(dining_table.restaurant, other_restaurant)

    def test_dining_table_qr_token_must_be_unique(self):
        DiningTable.objects.create(
            restaurant=self.restaurant,
            table_number='A1',
            qr_token='token-sama',
        )

        with self.assertRaises(IntegrityError):
            DiningTable.objects.create(
                restaurant=self.restaurant,
                table_number='A2',
                qr_token='token-sama',
            )

    def test_dining_table_is_registered_in_django_admin(self):
        self.assertIn(DiningTable, admin.site._registry)


class MenuAppearanceThemeModelTests(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Kedai Tema',
            slug='kedai-tema',
        )

    def test_theme_can_be_created_with_default_design_tokens(self):
        theme = MenuAppearanceTheme.objects.create(restaurant=self.restaurant)

        self.assertEqual(theme.restaurant, self.restaurant)
        self.assertEqual(theme.primary_color, '#1B4332')
        self.assertEqual(theme.secondary_color, '#D8F3DC')
        self.assertEqual(theme.accent_color, '#E07A5F')
        self.assertEqual(theme.background_color, '#F7F5F2')
        self.assertEqual(theme.text_color, '#1F2933')
        self.assertEqual(theme.card_color, '#FFFFFF')
        self.assertEqual(theme.font_family, 'Plus Jakarta Sans')
        self.assertEqual(theme.layout_style, MenuAppearanceTheme.LayoutStyle.GRID)
        self.assertEqual(theme.header_style, MenuAppearanceTheme.HeaderStyle.ROUNDED)
        self.assertTrue(theme.show_category_tabs)
        self.assertIsNotNone(theme.created_at)
        self.assertIsNotNone(theme.updated_at)

    def test_theme_string_representation_includes_restaurant(self):
        theme = MenuAppearanceTheme.objects.create(restaurant=self.restaurant)

        self.assertEqual(str(theme), 'Tema Menu - Kedai Tema')

    def test_theme_is_one_to_one_per_restaurant(self):
        MenuAppearanceTheme.objects.create(restaurant=self.restaurant)

        with self.assertRaises(IntegrityError):
            MenuAppearanceTheme.objects.create(restaurant=self.restaurant)

    def test_theme_is_registered_in_django_admin(self):
        self.assertIn(MenuAppearanceTheme, admin.site._registry)
