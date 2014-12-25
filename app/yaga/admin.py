from __future__ import absolute_import, division, unicode_literals

from django.contrib import admin

from .models import Code, Group, Post, Member


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


class PostAdmin(
    admin.ModelAdmin
):
    list_display = (
        'user', 'attachment', 'group', 'ready', 'created_at', 'ready_at'
    )

    ordering = ('-created_at',)

    list_filter = ('ready',)


class MemberAdmin(
    admin.ModelAdmin
):
    list_display = ('user', 'group', 'mute', 'joined_at')


admin.site.register(Group, GroupAdmin)
admin.site.register(Code, CodeAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Member, MemberAdmin)
