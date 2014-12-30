from __future__ import absolute_import, division, unicode_literals

from django.contrib import admin

from .models import Code, Group, Post, Member


class CodeAdmin(
    admin.ModelAdmin
):
    list_display = ('phone', 'request_id', 'expire_at')

    ordering = ('-expire_at',)

    search_fields = ('phone', 'request_id',)


class GroupAdmin(
    admin.ModelAdmin
):
    list_display = ('name', 'created_at', 'members_count')

    ordering = ('-created_at',)

    search_fields = ('name',)


class PostAdmin(
    admin.ModelAdmin
):
    list_display = (
        'user', 'attachment', 'group', 'mime',
        'ready', 'created_at', 'ready_at'
    )

    ordering = ('-created_at',)

    list_filter = ('ready', 'mime')

    search_fields = ('attachment',)


class MemberAdmin(
    admin.ModelAdmin
):
    list_display = ('user', 'group', 'mute', 'joined_at')

    ordering = ('-joined_at', 'mute')


admin.site.register(Group, GroupAdmin)
admin.site.register(Code, CodeAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Member, MemberAdmin)
