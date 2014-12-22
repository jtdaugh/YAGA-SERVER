from __future__ import absolute_import, division, unicode_literals

from django.contrib import admin

from .models import Code


class CodeAdmin(
    admin.ModelAdmin
):
    list_display = ('request_id', 'phone', 'expire_at')

    ordering = ('-expire_at',)


admin.site.register(Code, CodeAdmin)
