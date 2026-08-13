from django.contrib import admin
from django.db import IntegrityError
from django.test import TestCase

from menus.models import MenuItem
from orders.models import Order, OrderItem
from orders.services import create_order_from_cart
from restaurants.models import DiningTable, Restaurant


class OrderModelTests(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Kedai Order',
            slug='kedai-order',
        )
        self.table = DiningTable.objects.create(
            restaurant=self.restaurant,
            table_number='A1',
        )

    def test_order_can_be_created_with_required_fields(self):
        order = Order.objects.create(
            restaurant=self.restaurant,
            dining_table=self.table,
            code='ORD-0001',
            customer_name='Budi',
        )

        self.assertEqual(order.restaurant, self.restaurant)
        self.assertEqual(order.dining_table, self.table)
        self.assertEqual(order.code, 'ORD-0001')
        self.assertEqual(order.customer_name, 'Budi')
        self.assertEqual(order.status, Order.Status.NEW)
        self.assertEqual(order.payment_status, Order.PaymentStatus.UNPAID)
        self.assertEqual(order.notes, '')
        self.assertEqual(order.total_amount, 0)
        self.assertIsNotNone(order.created_at)
        self.assertIsNotNone(order.updated_at)

    def test_order_string_representation_includes_code_and_table_number(self):
        order = Order.objects.create(
            restaurant=self.restaurant,
            dining_table=self.table,
            code='ORD-0002',
        )

        self.assertEqual(str(order), 'ORD-0002 - Meja A1')

    def test_order_code_must_be_unique_per_restaurant(self):
        Order.objects.create(
            restaurant=self.restaurant,
            dining_table=self.table,
            code='ORD-0003',
        )

        with self.assertRaises(IntegrityError):
            Order.objects.create(
                restaurant=self.restaurant,
                dining_table=self.table,
                code='ORD-0003',
            )

    def test_same_order_code_is_allowed_for_different_restaurants(self):
        other_restaurant = Restaurant.objects.create(
            name='Cabang Order',
            slug='cabang-order',
        )
        other_table = DiningTable.objects.create(
            restaurant=other_restaurant,
            table_number='A1',
        )
        Order.objects.create(
            restaurant=self.restaurant,
            dining_table=self.table,
            code='ORD-0004',
        )
        order = Order.objects.create(
            restaurant=other_restaurant,
            dining_table=other_table,
            code='ORD-0004',
        )

        self.assertEqual(order.restaurant, other_restaurant)

    def test_order_is_registered_in_django_admin(self):
        self.assertIn(Order, admin.site._registry)


class OrderItemModelTests(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Kedai Order Item',
            slug='kedai-order-item',
        )
        self.table = DiningTable.objects.create(
            restaurant=self.restaurant,
            table_number='B2',
        )
        self.menu_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            name='Nasi Goreng',
            slug='nasi-goreng',
            price=18000,
        )
        self.order = Order.objects.create(
            restaurant=self.restaurant,
            dining_table=self.table,
            code='ORD-ITEM-0001',
        )

    def test_order_item_can_be_created_with_required_fields(self):
        order_item = OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            item_name='Nasi Goreng',
            unit_price=18000,
            quantity=2,
        )

        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.menu_item, self.menu_item)
        self.assertEqual(order_item.item_name, 'Nasi Goreng')
        self.assertEqual(order_item.unit_price, 18000)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.notes, '')
        self.assertIsNotNone(order_item.created_at)

    def test_order_item_line_total_multiplies_price_and_quantity(self):
        order_item = OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            item_name='Nasi Goreng',
            unit_price=18000,
            quantity=3,
        )

        self.assertEqual(order_item.line_total, 54000)

    def test_order_total_amount_sums_all_order_items(self):
        OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            item_name='Nasi Goreng',
            unit_price=18000,
            quantity=2,
        )
        OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            item_name='Es Teh',
            unit_price=5000,
            quantity=1,
        )

        self.assertEqual(self.order.calculate_total_amount(), 41000)

    def test_order_item_string_representation_includes_quantity_and_name(self):
        order_item = OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            item_name='Nasi Goreng',
            unit_price=18000,
            quantity=2,
        )

        self.assertEqual(str(order_item), '2x Nasi Goreng')

    def test_order_item_is_registered_in_django_admin(self):
        self.assertIn(OrderItem, admin.site._registry)


class CreateOrderFromCartServiceTests(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Kedai Service',
            slug='kedai-service',
        )
        self.table = DiningTable.objects.create(
            restaurant=self.restaurant,
            table_number='C3',
        )
        self.rice = MenuItem.objects.create(
            restaurant=self.restaurant,
            name='Nasi Service',
            slug='nasi-service',
            price=12000,
        )
        self.tea = MenuItem.objects.create(
            restaurant=self.restaurant,
            name='Teh Service',
            slug='teh-service',
            price=5000,
        )

    def test_create_order_from_cart_creates_order_items_and_total(self):
        order = create_order_from_cart(
            table=self.table,
            cart_items=[
                {'menu_item': self.rice, 'quantity': 2, 'note': 'tanpa sambal'},
                {'menu_item': self.tea, 'quantity': 1},
            ],
            customer_name='Ani',
            customer_note='Cepat ya',
        )

        self.assertEqual(order.restaurant, self.restaurant)
        self.assertEqual(order.dining_table, self.table)
        self.assertTrue(order.code.startswith('ORD-'))
        self.assertEqual(order.customer_name, 'Ani')
        self.assertEqual(order.notes, 'Cepat ya')
        self.assertEqual(order.total_amount, 29000)

        items = list(order.items.order_by('created_at'))
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].menu_item, self.rice)
        self.assertEqual(items[0].item_name, 'Nasi Service')
        self.assertEqual(items[0].unit_price, 12000)
        self.assertEqual(items[0].quantity, 2)
        self.assertEqual(items[0].notes, 'tanpa sambal')
        self.assertEqual(items[0].line_total, 24000)
        self.assertEqual(items[1].item_name, 'Teh Service')
        self.assertEqual(items[1].unit_price, 5000)
        self.assertEqual(items[1].quantity, 1)

    def test_create_order_from_cart_rejects_empty_cart(self):
        with self.assertRaisesMessage(ValueError, 'Cart tidak boleh kosong.'):
            create_order_from_cart(table=self.table, cart_items=[])

    def test_create_order_from_cart_rejects_unavailable_menu_item(self):
        self.rice.is_available = False
        self.rice.save(update_fields=['is_available'])

        with self.assertRaisesMessage(
            ValueError,
            'Menu Nasi Service sedang tidak tersedia.',
        ):
            create_order_from_cart(
                table=self.table,
                cart_items=[{'menu_item': self.rice, 'quantity': 1}],
            )

    def test_create_order_from_cart_rejects_inactive_menu_item(self):
        self.rice.is_active = False
        self.rice.save(update_fields=['is_active'])

        with self.assertRaisesMessage(
            ValueError,
            'Menu Nasi Service sedang tidak tersedia.',
        ):
            create_order_from_cart(
                table=self.table,
                cart_items=[{'menu_item': self.rice, 'quantity': 1}],
            )

    def test_create_order_from_cart_rejects_menu_from_different_restaurant(self):
        other_restaurant = Restaurant.objects.create(
            name='Kedai Lain',
            slug='kedai-lain',
        )
        other_menu = MenuItem.objects.create(
            restaurant=other_restaurant,
            name='Menu Beda Resto',
            slug='menu-beda-resto',
            price=15000,
        )

        with self.assertRaisesMessage(
            ValueError,
            'Menu harus berasal dari restoran meja yang sama.',
        ):
            create_order_from_cart(
                table=self.table,
                cart_items=[{'menu_item': other_menu, 'quantity': 1}],
            )

    def test_create_order_from_cart_rejects_quantity_less_than_one(self):
        with self.assertRaisesMessage(ValueError, 'Quantity menu minimal 1.'):
            create_order_from_cart(
                table=self.table,
                cart_items=[{'menu_item': self.rice, 'quantity': 0}],
            )

    def test_create_order_from_cart_keeps_price_snapshot_after_menu_price_changes(self):
        order = create_order_from_cart(
            table=self.table,
            cart_items=[{'menu_item': self.rice, 'quantity': 1}],
        )

        self.rice.price = 99000
        self.rice.save(update_fields=['price'])

        order_item = order.items.get()
        self.assertEqual(order_item.item_name, 'Nasi Service')
        self.assertEqual(order_item.unit_price, 12000)
        self.assertEqual(order.total_amount, 12000)


class OrderStatusTransitionTests(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Kedai Status',
            slug='kedai-status',
        )
        self.table = DiningTable.objects.create(
            restaurant=self.restaurant,
            table_number='A1',
        )
        self.order = Order.objects.create(
            restaurant=self.restaurant,
            dining_table=self.table,
            code='ORD-TRANS-001',
        )

    def test_new_to_processing_is_allowed(self):
        from orders.services import transition_order_status

        result = transition_order_status(
            order=self.order,
            new_status=Order.Status.PROCESSING,
        )
        self.assertEqual(result.status, Order.Status.PROCESSING)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.PROCESSING)

    def test_new_to_completed_is_rejected(self):
        from orders.services import (
            OrderStatusTransitionError,
            transition_order_status,
        )

        with self.assertRaises(OrderStatusTransitionError):
            transition_order_status(
                order=self.order,
                new_status=Order.Status.COMPLETED,
            )

    def test_processing_to_cancelled_is_allowed(self):
        from orders.services import transition_order_status

        self.order.status = Order.Status.PROCESSING
        self.order.save(update_fields=['status'])

        result = transition_order_status(
            order=self.order,
            new_status=Order.Status.CANCELLED,
        )
        self.assertEqual(result.status, Order.Status.CANCELLED)

    def test_ready_to_completed_is_allowed(self):
        from orders.services import transition_order_status

        self.order.status = Order.Status.READY
        self.order.save(update_fields=['status'])

        result = transition_order_status(
            order=self.order,
            new_status=Order.Status.COMPLETED,
        )
        self.assertEqual(result.status, Order.Status.COMPLETED)

    def test_completed_cannot_transition(self):
        from orders.services import (
            OrderStatusTransitionError,
            transition_order_status,
        )

        self.order.status = Order.Status.COMPLETED
        self.order.save(update_fields=['status'])

        with self.assertRaises(OrderStatusTransitionError):
            transition_order_status(
                order=self.order,
                new_status=Order.Status.READY,
            )

    def test_invalid_status_value_is_rejected(self):
        from orders.services import (
            OrderStatusTransitionError,
            transition_order_status,
        )

        with self.assertRaises(OrderStatusTransitionError):
            transition_order_status(
                order=self.order,
                new_status='not-a-status',
            )

    def test_can_transition_status_accepts_string_status(self):
        from orders.services import can_transition_status

        self.assertTrue(can_transition_status('new', 'processing'))
        self.assertFalse(can_transition_status('new', 'completed'))
        self.assertTrue(can_transition_status('processing', 'ready'))
