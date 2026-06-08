import uuid

from django.db import models


def generate_qr_token():
    return uuid.uuid4().hex


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
