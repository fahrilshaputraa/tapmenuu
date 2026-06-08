from django.contrib import admin

from menus.models import MenuCategory, MenuItem


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
