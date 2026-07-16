from django.contrib import admin

from restaurants.models import DiningTable, MenuAppearanceTheme, Restaurant


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug', 'phone')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MenuAppearanceTheme)
class MenuAppearanceThemeAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'primary_color', 'layout_style', 'header_style', 'updated_at')
    list_filter = ('layout_style', 'header_style', 'button_style', 'show_category_tabs')
    search_fields = ('restaurant__name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DiningTable)
class DiningTableAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'restaurant', 'capacity', 'is_active', 'created_at')
    list_filter = ('restaurant', 'is_active', 'created_at')
    search_fields = ('table_number', 'restaurant__name')
    readonly_fields = ('created_at', 'updated_at')
