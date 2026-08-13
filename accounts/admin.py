from django.contrib import admin

from accounts.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'restaurant')
    list_filter = ('role', 'restaurant')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',)
