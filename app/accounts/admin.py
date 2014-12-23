from __future__ import absolute_import, division, unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from .forms import UserChangeForm, UserCreationForm
from .models import Token


class UserAdmin(
    UserAdmin
):
    fieldsets = (
        (None, {
            'fields': (
                'phone',
                'name',
                'password',
                'verified'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        (_('Important dates'), {
            'fields': (
                'last_login',
                'date_joined'
            )
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone',
                'name',
                'password1',
                'password2',
                'verified'
            )
        }),
    )

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        'phone', 'name', 'verified', 'is_active', 'is_staff', 'is_superuser'
    )

    list_filter = (
        'verified', 'is_active', 'is_staff', 'is_superuser', 'groups'
    )

    search_fields = ('phone', 'name')

    ordering = ('-date_joined',)

    filter_horizontal = ('groups', 'user_permissions')


class TokenAdmin(
    admin.ModelAdmin
):
    list_display = ('user', 'key', 'created_at')

    ordering = ('-created_at',)


admin.site.register(get_user_model(), UserAdmin)
admin.site.register(Token, TokenAdmin)
