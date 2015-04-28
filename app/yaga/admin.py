from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from .models import (
    Code, Contact, Device, Group, Like, Member, MonkeyUser, Post
)


class CodeModelAdmin(
    admin.ModelAdmin
):
    list_display = ('phone', 'request_id', 'expire_at')

    ordering = ('-expire_at',)

    search_fields = ('phone', 'request_id',)


class MemberTabularInline(
    admin.TabularInline
):
    model = Member


class PostBaseInlineFormSet(
    BaseInlineFormSet
):
    def get_queryset(self):
        return super(PostBaseInlineFormSet, self).get_queryset().filter(
            ready=True,
            deleted=False
        )


class PostTabularInline(
    admin.TabularInline
):
    model = Post

    formset = PostBaseInlineFormSet

    fields = ('name', 'user', 'attachment', 'attachment_preview')


class GroupModelAdmin(
    admin.ModelAdmin
):
    list_display = ('pk', 'name', 'created_at', 'members_count', 'posts_count')

    ordering = ('-created_at',)

    search_fields = ('name', 'id')

    inlines = (MemberTabularInline, PostTabularInline)


class PostModelAdmin(
    admin.ModelAdmin
):
    list_display = (
        'pk', 'name', 'user', 'likes', 'group',
        'ready', 'deleted', 'created_at'
    )

    ordering = ('-created_at',)

    list_filter = ('ready', 'deleted')

    search_fields = ('attachment', 'name', 'id')


class MemberModelAdmin(
    admin.ModelAdmin
):
    list_display = ('user', 'group', 'mute', 'joined_at')

    list_filter = ('mute',)

    ordering = ('-joined_at', 'mute')


class LikeModelAdmin(
    admin.ModelAdmin
):
    list_display = ('user', 'post',)

    ordering = ('-created_at',)


class DeviceModelAdmin(
    admin.ModelAdmin
):
    list_display = ('user', 'token', 'vendor', 'locale')

    list_filter = ('vendor', 'locale')

    search_fields = ('token',)


class ContactModelAdmin(
    admin.ModelAdmin
):
    list_display = ('pk', 'user')


class MonkeyUserModelAdmin(
    admin.ModelAdmin
):
    list_display = ('pk', 'user')


admin.site.register(Group, GroupModelAdmin)
admin.site.register(Code, CodeModelAdmin)
admin.site.register(Contact, ContactModelAdmin)
admin.site.register(Post, PostModelAdmin)
admin.site.register(Member, MemberModelAdmin)
admin.site.register(Like, LikeModelAdmin)
admin.site.register(Device, DeviceModelAdmin)
admin.site.register(MonkeyUser, MonkeyUserModelAdmin)
