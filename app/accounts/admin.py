from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _
from hijack.admin import HijackUserAdminMixin

from app.admin import ForceSuperuserAccess

from .filters import PasswordSimpleListFilter
from .forms import UserChangeForm, UserCreationForm
from .models import Token


class TokenTabularInline(
    admin.TabularInline
):
    model = Token


class UserModelAdmin(
    ForceSuperuserAccess, BaseUserAdmin, HijackUserAdminMixin
):
    def lookup_allowed(self, lookup, value):
        if lookup.startswith('password'):
            return True

        return super(UserModelAdmin, self).lookup_allowed(lookup, value)

    fieldsets = (
        (None, {
            'fields': (
                'phone',
                'name',
                'password'
            )
        }),
        (_('Optional'), {
            'fields': (
                'verified',
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
                'verified_at',
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
                'password2'
            )
        }),
    )

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        'phone', 'name', 'verified',
        'is_active', 'is_staff', 'is_superuser', 'hijack_field'
    )

    list_filter = (
        'verified', 'is_active', 'is_staff', 'is_superuser', 'groups',
        PasswordSimpleListFilter
    )

    search_fields = ('phone', 'name')

    ordering = ('-date_joined',)

    filter_horizontal = ('groups', 'user_permissions')

    inlines = (TokenTabularInline,)


class TokenModelAdmin(
    ForceSuperuserAccess, admin.ModelAdmin
):
    list_display = ('user', 'key', 'created_at')

    ordering = ('-created_at',)

    search_fields = ('key',)

    raw_id_fields = ('user',)


admin.site.register(get_user_model(), UserModelAdmin)
admin.site.register(Token, TokenModelAdmin)
