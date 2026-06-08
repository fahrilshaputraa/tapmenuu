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
    image = models.ImageField(upload_to='menus/items/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
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
