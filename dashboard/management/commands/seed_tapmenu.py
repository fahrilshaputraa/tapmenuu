from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from menus.models import MenuCategory, MenuItem
from orders.models import Order, OrderItem
from payments.models import Payment
from restaurants.models import DiningTable, Restaurant


class Command(BaseCommand):
    help = 'Seed data development TapMenu untuk smoke test end-to-end.'

    def handle(self, *args, **options):
        owner, _ = User.objects.get_or_create(
            username='owner',
            defaults={
                'email': 'owner@tapmenu.test',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        owner.set_password('password12345')
        owner.is_staff = True
        owner.save()

        restaurant, _ = Restaurant.objects.get_or_create(
            slug='warung-bu-dewi',
            defaults={
                'name': 'Warung Bu Dewi',
                'description': 'Warung makan rumahan dengan menu digital TapMenu.',
                'address': 'Jl. Merdeka No. 45, Bandung',
                'phone': '081234567890',
            },
        )

        tables = []
        for number in ['1', '2', '3', '4']:
            table, _ = DiningTable.objects.get_or_create(
                restaurant=restaurant,
                table_number=number,
                defaults={'capacity': 2},
            )
            tables.append(table)

        category_names = ['Makanan', 'Minuman']
        categories = {}
        for index, name in enumerate(category_names, start=1):
            category, _ = MenuCategory.objects.get_or_create(
                restaurant=restaurant,
                slug=slugify(name),
                defaults={'name': name, 'sort_order': index},
            )
            categories[name] = category

        menu_specs = [
            ('Ayam Geprek', 'Makanan', 15000),
            ('Nasi Goreng Kampung', 'Makanan', 18000),
            ('Es Teh Jumbo', 'Minuman', 6000),
            ('Es Kopi Susu', 'Minuman', 12000),
        ]
        items = []
        for index, (name, category_name, price) in enumerate(menu_specs, start=1):
            item, _ = MenuItem.objects.get_or_create(
                restaurant=restaurant,
                slug=slugify(name),
                defaults={
                    'category': categories[category_name],
                    'name': name,
                    'price': price,
                    'sort_order': index,
                    'description': f'Menu favorit: {name}',
                },
            )
            items.append(item)

        order, created = Order.objects.get_or_create(
            restaurant=restaurant,
            code='ORD-SEED-001',
            defaults={
                'dining_table': tables[0],
                'customer_name': 'Customer Demo',
                'status': Order.Status.PREPARING,
                'total_amount': 0,
            },
        )
        if created:
            total = 0
            for item in items[:2]:
                order_item = OrderItem.objects.create(
                    order=order,
                    menu_item=item,
                    item_name=item.name,
                    unit_price=item.price,
                    quantity=1,
                )
                total += order_item.line_total
            order.total_amount = total
            order.save(update_fields=['total_amount', 'updated_at'])

        Payment.objects.get_or_create(
            order=order,
            reference='PAY-SEED-001',
            defaults={
                'method': Payment.Method.QRIS,
                'amount': order.total_amount,
                'provider': 'dummy',
                'provider_reference': 'DUMMY-SEED-001',
                'notes': 'qr_string=DUMMY-QRIS-SEED',
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                'Seed data TapMenu siap. Login: owner / password12345',
            ),
        )
