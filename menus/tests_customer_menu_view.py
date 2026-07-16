from django.test import TestCase
from django.urls import reverse

from menus.models import (
    MenuCategory,
    MenuItem,
    MenuItemVariantGroup,
    MenuItemVariantOption,
)
from menus.views import CUSTOMER_CART_SESSION_KEY
from orders.models import Order
from payments.models import Payment
from restaurants.models import DiningTable, MenuAppearanceTheme, Restaurant


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

    def test_customer_menu_renders_theme_css_variables_from_restaurant_theme(self):
        MenuAppearanceTheme.objects.create(
            restaurant=self.restaurant,
            primary_color='#0F766E',
            secondary_color='#CCFBF1',
            accent_color='#F97316',
            background_color='#FFF7ED',
            text_color='#111827',
            card_color='#FFFFFF',
            font_family='Inter',
            layout_style=MenuAppearanceTheme.LayoutStyle.COMPACT,
            header_style=MenuAppearanceTheme.HeaderStyle.MINIMAL,
            button_style=MenuAppearanceTheme.ButtonStyle.PILL,
        )

        response = self.client.get(
            reverse('customer_menu', kwargs={'qr_token': self.table.qr_token}),
        )

        self.assertEqual(response.context['appearance_theme'].primary_color, '#0F766E')
        self.assertContains(response, '--menu-primary: #0F766E')
        self.assertContains(response, '--menu-secondary: #CCFBF1')
        self.assertContains(response, '--menu-accent: #F97316')
        self.assertContains(response, '--menu-bg: #FFF7ED')
        self.assertContains(response, '--menu-text: #111827')
        self.assertContains(response, 'data-layout-style="compact"')
        self.assertContains(response, 'data-header-style="minimal"')
        self.assertContains(response, 'data-button-style="pill"')

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
        self.assertContains(response, 'Tambah ke Keranjang')
        self.assertContains(response, 'data-open-cart-sheet')
        self.assertContains(response, 'order-sheet-')
        self.assertContains(response, 'Jumlah Pesanan')
        self.assertContains(response, 'Catatan Pesanan')

    def test_customer_menu_renders_order_sheets_outside_menu_cards(self):
        response = self.client.get(
            reverse('customer_menu', kwargs={'qr_token': self.table.qr_token}),
        )
        html = response.content.decode()
        article_start = html.index('<article')
        article_end = html.index('</article>', article_start)
        first_article_html = html[article_start:article_end]
        sheet_start = html.index('id="order-sheet-')

        self.assertNotIn('order-sheet fixed inset-0', first_article_html)
        self.assertGreater(sheet_start, article_end)
        self.assertContains(response, 'data-sheet-panel')
        self.assertContains(response, 'data-sheet-drag-zone')

    def test_customer_menu_shows_favorite_new_badges_and_variant_choices_in_sheet(self):
        self.item.is_favorite = True
        self.item.is_new = True
        self.item.save(update_fields=['is_favorite', 'is_new'])
        group = MenuItemVariantGroup.objects.create(
            menu_item=self.item,
            name='Level Pedas',
            type='radio',
        )
        MenuItemVariantOption.objects.create(
            group=group,
            name='Pedas',
            price_adjustment=2000,
        )

        response = self.client.get(
            reverse('customer_menu', kwargs={'qr_token': self.table.qr_token}),
        )

        self.assertContains(response, 'Favorit')
        self.assertContains(response, 'Baru')
        self.assertContains(response, 'Level Pedas')
        self.assertContains(response, 'Pedas')
        self.assertContains(response, '+ Rp 2.000')

    def test_customer_cart_add_stores_variant_choices_and_uses_adjusted_price(self):
        group = MenuItemVariantGroup.objects.create(
            menu_item=self.item,
            name='Level Pedas',
            type='radio',
        )
        option = MenuItemVariantOption.objects.create(
            group=group,
            name='Pedas',
            price_adjustment=2000,
        )

        response = self.client.post(
            reverse(
                'customer_cart_add',
                kwargs={
                    'qr_token': self.table.qr_token,
                    'item_id': self.item.id,
                },
            ),
            {
                'quantity': '2',
                'note': 'jangan pakai es',
                'variant_options': [str(option.id)],
            },
        )

        self.assertRedirects(
            response,
            reverse('customer_menu', kwargs={'qr_token': self.table.qr_token}),
        )
        cart_items = self.client.session[CUSTOMER_CART_SESSION_KEY]['items']
        cart_item = next(iter(cart_items.values()))
        self.assertEqual(cart_item['quantity'], 2)
        self.assertEqual(cart_item['note'], 'jangan pakai es')
        self.assertEqual(cart_item['variant_option_ids'], [option.id])

        cart_response = self.client.get(
            reverse('customer_cart', kwargs={'qr_token': self.table.qr_token}),
        )
        self.assertContains(cart_response, 'Level Pedas: Pedas')
        self.assertContains(cart_response, 'Rp 14.000')

    def test_customer_menu_renders_filter_tabs_with_all_tab_and_category_panels(self):
        response = self.client.get(
            reverse('customer_menu', kwargs={'qr_token': self.table.qr_token}),
        )

        self.assertContains(response, 'data-menu-tab="all"')
        self.assertContains(response, 'Semua')
        self.assertContains(response, f'data-menu-tab="cat-{self.category.id}"')
        self.assertContains(response, f'data-menu-panel="cat-{self.category.id}"')
        self.assertContains(response, 'data-default-tab-class')
        self.assertContains(response, 'data-active-tab-class')

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
        cart_item = next(iter(cart['items'].values()))
        self.assertEqual(cart_item['quantity'], 2)
        self.assertEqual(cart_item['note'], 'tanpa gula')

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

    def test_customer_menu_links_to_dedicated_cart_page_when_cart_has_items(self):
        self._put_item_in_session_cart(quantity=2)

        response = self.client.get(
            reverse('customer_menu', kwargs={'qr_token': self.table.qr_token}),
        )

        self.assertContains(response, 'Buka halaman keranjang')
        self.assertContains(
            response,
            reverse('customer_cart', kwargs={'qr_token': self.table.qr_token}),
        )
        self.assertNotContains(response, 'Nama Customer')
        self.assertNotContains(response, 'Metode Pembayaran')

    def test_customer_cart_page_is_dedicated_checkout_without_menu_list(self):
        self._put_item_in_session_cart(quantity=2, note='tanpa gula')

        response = self.client.get(
            reverse('customer_cart', kwargs={'qr_token': self.table.qr_token}),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pesanan Anda')
        self.assertContains(response, 'Es Teh Manis')
        self.assertContains(response, 'tanpa gula')
        self.assertContains(response, 'Rp 10.000')
        self.assertContains(
            response,
            reverse('customer_checkout', kwargs={'qr_token': self.table.qr_token}),
        )
        self.assertContains(response, 'Nama Customer')
        self.assertContains(response, 'Metode Pembayaran')
        self.assertContains(response, 'QRIS')
        self.assertNotContains(response, 'Pilih menu favorit')
        self.assertNotContains(response, 'Tambah ke Keranjang')

    def test_customer_cart_page_renders_swipe_delete_action_for_each_item(self):
        self._put_item_in_session_cart(quantity=2, note='tanpa gula')

        response = self.client.get(
            reverse('customer_cart', kwargs={'qr_token': self.table.qr_token}),
        )

        self.assertContains(response, 'data-cart-swipe-item')
        self.assertContains(response, 'data-cart-swipe-content')
        self.assertContains(response, 'data-cart-delete-action')
        self.assertContains(response, 'data-cart-qty-control')
        self.assertContains(response, 'aria-label="Kurangi qty Es Teh Manis"')
        self.assertContains(response, 'aria-label="Tambah qty Es Teh Manis"')
        self.assertContains(response, 'Geser kiri untuk hapus')
        self.assertContains(response, 'Hapus')
        self.assertContains(
            response,
            reverse(
                'customer_cart_remove',
                kwargs={'qr_token': self.table.qr_token, 'line_key': str(self.item.id)},
            ),
        )
        self.assertContains(
            response,
            reverse(
                'customer_cart_quantity',
                kwargs={'qr_token': self.table.qr_token, 'line_key': str(self.item.id)},
            ),
        )

    def test_customer_cart_quantity_update_increments_line_item_quantity(self):
        self._put_item_in_session_cart(quantity=2)

        response = self.client.post(
            reverse(
                'customer_cart_quantity',
                kwargs={'qr_token': self.table.qr_token, 'line_key': str(self.item.id)},
            ),
            {'action': 'increment'},
        )

        self.assertRedirects(
            response,
            reverse('customer_cart', kwargs={'qr_token': self.table.qr_token}),
        )
        cart_item = self.client.session[CUSTOMER_CART_SESSION_KEY]['items'][str(self.item.id)]
        self.assertEqual(cart_item['quantity'], 3)

    def test_customer_cart_quantity_update_decrements_line_item_quantity(self):
        self._put_item_in_session_cart(quantity=2)

        self.client.post(
            reverse(
                'customer_cart_quantity',
                kwargs={'qr_token': self.table.qr_token, 'line_key': str(self.item.id)},
            ),
            {'action': 'decrement'},
        )

        cart_item = self.client.session[CUSTOMER_CART_SESSION_KEY]['items'][str(self.item.id)]
        self.assertEqual(cart_item['quantity'], 1)

    def test_customer_cart_quantity_update_removes_line_when_decrementing_from_one(self):
        self._put_item_in_session_cart(quantity=1)

        response = self.client.post(
            reverse(
                'customer_cart_quantity',
                kwargs={'qr_token': self.table.qr_token, 'line_key': str(self.item.id)},
            ),
            {'action': 'decrement'},
        )

        self.assertRedirects(
            response,
            reverse('customer_cart', kwargs={'qr_token': self.table.qr_token}),
        )
        self.assertIsNone(self.client.session.get(CUSTOMER_CART_SESSION_KEY))

    def test_customer_cart_remove_deletes_line_item_from_session_and_redirects_to_cart(self):
        self._put_item_in_session_cart(quantity=2, note='tanpa gula')

        response = self.client.post(
            reverse(
                'customer_cart_remove',
                kwargs={'qr_token': self.table.qr_token, 'line_key': str(self.item.id)},
            ),
        )

        self.assertRedirects(
            response,
            reverse('customer_cart', kwargs={'qr_token': self.table.qr_token}),
        )
        cart = self.client.session.get(CUSTOMER_CART_SESSION_KEY)
        self.assertIsNone(cart)

    def test_customer_cart_remove_ignores_different_table_cart(self):
        self._put_item_in_session_cart(quantity=2)
        other_table = DiningTable.objects.create(
            restaurant=self.restaurant,
            table_number='B2',
            capacity=2,
            qr_token='qr-meja-b2',
        )

        response = self.client.post(
            reverse(
                'customer_cart_remove',
                kwargs={'qr_token': other_table.qr_token, 'line_key': str(self.item.id)},
            ),
        )

        self.assertRedirects(
            response,
            reverse('customer_cart', kwargs={'qr_token': other_table.qr_token}),
        )
        self.assertIn(str(self.item.id), self.client.session[CUSTOMER_CART_SESSION_KEY]['items'])

    def test_customer_cart_page_renders_empty_state(self):
        response = self.client.get(
            reverse('customer_cart', kwargs={'qr_token': self.table.qr_token}),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Keranjang masih kosong')
        self.assertContains(
            response,
            reverse('customer_menu', kwargs={'qr_token': self.table.qr_token}),
        )

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
            reverse('customer_cart', kwargs={'qr_token': self.table.qr_token}),
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
