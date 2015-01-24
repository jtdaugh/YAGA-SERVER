from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib import admin

from .models import Code, Device, Group, Like, Member, Post


class CodeAdmin(
    admin.ModelAdmin
):
    list_display = ('phone', 'request_id', 'expire_at')

    ordering = ('-expire_at',)

    search_fields = ('phone', 'request_id',)


class GroupAdmin(
    admin.ModelAdmin
):
    list_display = ('pk', 'name', 'created_at', 'members_count', 'posts_count')

    ordering = ('-created_at',)

    search_fields = ('name', 'pk')


class PostAdmin(
    admin.ModelAdmin
):
    list_display = (
        'pk', 'name', 'user', 'likes', 'group', 'mime',
        'ready', 'deleted', 'updated_at'
    )

    ordering = ('-ready_at',)

    list_filter = ('ready', 'mime', 'deleted')

    search_fields = ('attachment', 'name', 'pk')


class MemberAdmin(
    admin.ModelAdmin
):
    list_display = ('user', 'group', 'mute', 'joined_at')

    ordering = ('-joined_at', 'mute')


class LikeAdmin(
    admin.ModelAdmin
):
    list_display = ('user', 'post',)

    ordering = ('-created_at',)


class DeviceAdmin(
    admin.ModelAdmin
):
    list_display = ('user', 'token', 'vendor', 'locale')

    list_filter = ('vendor', 'locale')


admin.site.register(Group, GroupAdmin)
admin.site.register(Code, CodeAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Device, DeviceAdmin)
