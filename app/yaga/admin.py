from __future__ import absolute_import, division, unicode_literals

from django.contrib import admin

from .models import Code, Group


class CodeAdmin(
    admin.ModelAdmin
):
    list_display = ('request_id', 'phone', 'expire_at')

    ordering = ('-expire_at',)


class GroupAdmin(
    admin.ModelAdmin
):
    list_display = ('name', 'created_at', 'members_count')

    ordering = ('-created_at',)


admin.site.register(Group, GroupAdmin)
admin.site.register(Code, CodeAdmin)
