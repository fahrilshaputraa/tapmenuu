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
        self.assertEqual(response.context['appearance_theme'].restaurant, self.restaurant)

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
