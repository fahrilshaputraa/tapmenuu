import uuid

from django.db import models


def generate_qr_token():
    return uuid.uuid4().hex


MENU_THEME_DEFAULTS = {
    'primary_color': '#1B4332',
    'secondary_color': '#D8F3DC',
    'accent_color': '#E07A5F',
    'background_color': '#F7F5F2',
    'text_color': '#1F2933',
    'card_color': '#FFFFFF',
    'font_family': 'Plus Jakarta Sans',
    'layout_style': 'grid',
    'header_style': 'rounded',
    'button_style': 'rounded',
    'show_category_tabs': True,
}


class Restaurant(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True)
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    logo = models.ImageField(upload_to='restaurants/logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class MenuAppearanceTheme(models.Model):
    class LayoutStyle(models.TextChoices):
        GRID = 'grid', 'Grid nyaman'
        COMPACT = 'compact', 'Compact'
        FEATURED = 'featured', 'Featured'

    class HeaderStyle(models.TextChoices):
        ROUNDED = 'rounded', 'Rounded'
        MINIMAL = 'minimal', 'Minimal'
        HERO = 'hero', 'Hero'

    class ButtonStyle(models.TextChoices):
        ROUNDED = 'rounded', 'Rounded'
        PILL = 'pill', 'Pill'
        SQUARE = 'square', 'Square'

    restaurant = models.OneToOneField(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='menu_theme',
    )
    primary_color = models.CharField(
        max_length=7,
        default=MENU_THEME_DEFAULTS['primary_color'],
    )
    secondary_color = models.CharField(
        max_length=7,
        default=MENU_THEME_DEFAULTS['secondary_color'],
    )
    accent_color = models.CharField(
        max_length=7,
        default=MENU_THEME_DEFAULTS['accent_color'],
    )
    background_color = models.CharField(
        max_length=7,
        default=MENU_THEME_DEFAULTS['background_color'],
    )
    text_color = models.CharField(
        max_length=7,
        default=MENU_THEME_DEFAULTS['text_color'],
    )
    card_color = models.CharField(
        max_length=7,
        default=MENU_THEME_DEFAULTS['card_color'],
    )
    font_family = models.CharField(
        max_length=80,
        default=MENU_THEME_DEFAULTS['font_family'],
    )
    layout_style = models.CharField(
        max_length=20,
        choices=LayoutStyle.choices,
        default=LayoutStyle.GRID,
    )
    header_style = models.CharField(
        max_length=20,
        choices=HeaderStyle.choices,
        default=HeaderStyle.ROUNDED,
    )
    button_style = models.CharField(
        max_length=20,
        choices=ButtonStyle.choices,
        default=ButtonStyle.ROUNDED,
    )
    show_category_tabs = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Menu appearance theme'
        verbose_name_plural = 'Menu appearance themes'

    def reset_to_defaults(self):
        for field_name, value in MENU_THEME_DEFAULTS.items():
            setattr(self, field_name, value)
        self.save(update_fields=[*MENU_THEME_DEFAULTS.keys(), 'updated_at'])

    def __str__(self):
        return f'Tema Menu - {self.restaurant.name}'


class DiningTable(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='dining_tables',
    )
    table_number = models.CharField(max_length=30)
    qr_token = models.SlugField(
        max_length=64,
        unique=True,
        default=generate_qr_token,
        editable=False,
    )
    capacity = models.PositiveSmallIntegerField(default=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['restaurant__name', 'table_number']
        constraints = [
            models.UniqueConstraint(
                fields=['restaurant', 'table_number'],
                name='unique_table_number_per_restaurant',
            ),
        ]

    def __str__(self):
        return f'{self.restaurant.name} - Meja {self.table_number}'
