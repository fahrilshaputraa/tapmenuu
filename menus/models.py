from django.db import models

from restaurants.models import Restaurant


class MenuCategory(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='menu_categories',
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=150)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['restaurant__name', 'sort_order', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['restaurant', 'slug'],
                name='unique_menu_category_slug_per_restaurant',
            ),
        ]
        verbose_name_plural = 'menu categories'

    def __str__(self):
        return f'{self.restaurant.name} - {self.name}'


class MenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='menu_items',
    )
    category = models.ForeignKey(
        MenuCategory,
        on_delete=models.SET_NULL,
        related_name='items',
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField()
    discount = models.PositiveSmallIntegerField(
        default=0, help_text='Diskon dalam persen (0-100)'
    )
    tax = models.PositiveSmallIntegerField(
        default=10, help_text='Pajak/PPN dalam persen'
    )
    stock = models.PositiveIntegerField(
        default=0, help_text='Jumlah stok (0 = tanpa batas)'
    )
    image = models.ImageField(upload_to='menus/items/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_favorite = models.BooleanField(default=False, help_text='Label menu favorit')
    is_new = models.BooleanField(default=False, help_text='Label menu baru')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['restaurant__name', 'category__sort_order', 'sort_order', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['restaurant', 'slug'],
                name='unique_menu_item_slug_per_restaurant',
            ),
        ]

    def __str__(self):
        return self.name


class MenuItemVariantGroup(models.Model):
    """Group of variants for a menu item (e.g., 'Level Pedas', 'Toping Tambahan')."""

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='variant_groups',
    )
    name = models.CharField(
        max_length=100, help_text='Nama grup varian, contoh: Level Pedas'
    )
    type = models.CharField(
        max_length=10,
        choices=[
            ('radio', 'Pilih Satu (Wajib)'),
            ('checkbox', 'Pilih Banyak (Opsional)'),
        ],
        default='radio',
    )
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f'{self.menu_item.name} - {self.name}'


class MenuItemVariantOption(models.Model):
    """Single option within a variant group (e.g., 'Pedas' +Rp 2000)."""

    group = models.ForeignKey(
        MenuItemVariantGroup,
        on_delete=models.CASCADE,
        related_name='options',
    )
    name = models.CharField(max_length=100, help_text='Nama opsi, contoh: Pedas')
    price_adjustment = models.IntegerField(
        default=0,
        help_text='Penyesuaian harga dalam Rupiah (positif = tambah, negatif = kurang)',
    )
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f'{self.group.name} - {self.name}'
