from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


class PasswordSimpleListFilter(
    SimpleListFilter
):
    title = _('Password')

    parameter_name = 'password'

    def lookups(self, request, model_admin):
        return (
            ('empty', _('empty')),
            ('unusable', _('unusable')),
            ('usable', _('usable')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'empty':
            return queryset.filter(
                password=''
            )
        elif self.value() == 'unusable':
            return queryset.filter(
                password__startswith='!'
            )
        elif self.value() == 'usable':
            return queryset.filter(
                password__contains='$'
            )
