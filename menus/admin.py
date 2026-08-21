from django.contrib import admin

from menus.models import (
    MenuCategory,
    MenuItem,
    MenuItemVariantGroup,
    MenuItemVariantOption,
)


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'sort_order', 'is_active', 'created_at')
    list_filter = ('restaurant', 'is_active', 'created_at')
    search_fields = ('name', 'slug', 'restaurant__name')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'restaurant',
        'category',
        'price',
        'is_available',
        'is_active',
        'created_at',
    )
    list_filter = ('restaurant', 'category', 'is_available', 'is_active', 'created_at')
    search_fields = ('name', 'slug', 'restaurant__name', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MenuItemVariantGroup)
class MenuItemVariantGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'menu_item', 'type', 'sort_order')
    list_filter = ('type',)
    search_fields = ('name', 'menu_item__name')


@admin.register(MenuItemVariantOption)
class MenuItemVariantOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'price_adjustment', 'sort_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'group__name')
