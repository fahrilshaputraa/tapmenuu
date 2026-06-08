from django.contrib import admin
from django.db import IntegrityError
from django.test import TestCase

from restaurants.models import DiningTable, Restaurant


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
