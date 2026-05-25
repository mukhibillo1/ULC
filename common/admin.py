from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from common import models

@admin.register(models.BaseUser)
class CustomUserAdmin(UserAdmin):
    model = models.BaseUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'role')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    search_fields = ('username', 'email')
    ordering = ('username',)
    filter_horizontal = ('user_permissions',)



