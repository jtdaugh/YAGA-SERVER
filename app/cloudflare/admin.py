from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib import admin

from app.admin import DisableNonSuperuserMixin

from .models import Mask


class MaskModelAdmin(
    DisableNonSuperuserMixin, admin.ModelAdmin
):
    list_display = ('value', 'created_at')

    search_fields = ('value',)


admin.site.register(Mask, MaskModelAdmin)
