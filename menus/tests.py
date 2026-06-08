from django.contrib import admin
from django.db import IntegrityError
from django.test import TestCase

from menus.models import MenuCategory, MenuItem
from restaurants.models import Restaurant


class MenuCategoryModelTests(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Kedai Menu',
            slug='kedai-menu',
        )

    def test_menu_category_can_be_created_with_required_fields(self):
        category = MenuCategory.objects.create(
            restaurant=self.restaurant,
            name='Minuman',
            slug='minuman',
        )

        self.assertEqual(category.restaurant, self.restaurant)
        self.assertEqual(category.name, 'Minuman')
        self.assertEqual(category.slug, 'minuman')
        self.assertEqual(category.sort_order, 0)
        self.assertTrue(category.is_active)
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)

    def test_menu_category_string_representation_includes_restaurant_and_name(self):
        category = MenuCategory.objects.create(
            restaurant=self.restaurant,
            name='Makanan',
            slug='makanan',
        )

        self.assertEqual(str(category), 'Kedai Menu - Makanan')

    def test_category_slug_must_be_unique_per_restaurant(self):
        MenuCategory.objects.create(
            restaurant=self.restaurant,
            name='Minuman',
            slug='minuman',
        )

        with self.assertRaises(IntegrityError):
            MenuCategory.objects.create(
                restaurant=self.restaurant,
                name='Minuman Lain',
                slug='minuman',
            )

    def test_same_category_slug_is_allowed_for_different_restaurants(self):
        other_restaurant = Restaurant.objects.create(
            name='Cabang Menu',
            slug='cabang-menu',
        )
        MenuCategory.objects.create(
            restaurant=self.restaurant,
            name='Minuman',
            slug='minuman',
        )
        category = MenuCategory.objects.create(
            restaurant=other_restaurant,
            name='Minuman',
            slug='minuman',
        )

        self.assertEqual(category.restaurant, other_restaurant)

    def test_menu_category_is_registered_in_django_admin(self):
        self.assertIn(MenuCategory, admin.site._registry)


class MenuItemModelTests(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Kedai Item',
            slug='kedai-item',
        )
        self.category = MenuCategory.objects.create(
            restaurant=self.restaurant,
            name='Minuman',
            slug='minuman',
        )

    def test_menu_item_can_be_created_with_required_fields(self):
        item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name='Es Teh Manis',
            slug='es-teh-manis',
            price=5000,
        )

        self.assertEqual(item.restaurant, self.restaurant)
        self.assertEqual(item.category, self.category)
        self.assertEqual(item.name, 'Es Teh Manis')
        self.assertEqual(item.slug, 'es-teh-manis')
        self.assertEqual(item.price, 5000)
        self.assertEqual(item.description, '')
        self.assertTrue(item.is_available)
        self.assertTrue(item.is_active)
        self.assertEqual(item.sort_order, 0)
        self.assertIsNotNone(item.created_at)
        self.assertIsNotNone(item.updated_at)

    def test_menu_item_category_is_optional(self):
        item = MenuItem.objects.create(
            restaurant=self.restaurant,
            name='Paket Rahasia',
            slug='paket-rahasia',
            price=15000,
        )

        self.assertIsNone(item.category)

    def test_menu_item_string_representation_returns_name(self):
        item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name='Kopi Susu',
            slug='kopi-susu',
            price=18000,
        )

        self.assertEqual(str(item), 'Kopi Susu')

    def test_menu_item_slug_must_be_unique_per_restaurant(self):
        MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name='Kopi Susu',
            slug='kopi-susu',
            price=18000,
        )

        with self.assertRaises(IntegrityError):
            MenuItem.objects.create(
                restaurant=self.restaurant,
                category=self.category,
                name='Kopi Susu Baru',
                slug='kopi-susu',
                price=20000,
            )

    def test_same_menu_item_slug_is_allowed_for_different_restaurants(self):
        other_restaurant = Restaurant.objects.create(
            name='Cabang Item',
            slug='cabang-item',
        )
        MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name='Kopi Susu',
            slug='kopi-susu',
            price=18000,
        )
        item = MenuItem.objects.create(
            restaurant=other_restaurant,
            name='Kopi Susu',
            slug='kopi-susu',
            price=18000,
        )

        self.assertEqual(item.restaurant, other_restaurant)

    def test_menu_item_is_registered_in_django_admin(self):
        self.assertIn(MenuItem, admin.site._registry)
