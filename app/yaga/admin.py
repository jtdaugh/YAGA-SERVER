from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from app.admin import ForceSuperuserAccess

from .models import (
    Code, Contact, Device, Group, Like, Member, MonkeyUser, Post, PostCopy
)


class CodeModelAdmin(
    ForceSuperuserAccess, admin.ModelAdmin
):
    list_display = ('phone', 'request_id', 'expire_at')

    ordering = ('-expire_at',)

    search_fields = ('phone', 'request_id',)

    date_hierarchy = 'expire_at'


class MemberTabularInline(
    admin.TabularInline
):
    model = Member

    raw_id_fields = ('user', 'creator',)


class PostBaseInlineFormSet(
    BaseInlineFormSet
):
    def get_queryset(self):
        return super(PostBaseInlineFormSet, self).get_queryset().filter(
            state__in=[Post.state_choices.READY, Post.state_choices.DELETED]
        )


class PostTabularInline(
    admin.TabularInline
):
    model = Post

    formset = PostBaseInlineFormSet

    fields = ('name', 'user', 'attachment', 'state')

    raw_id_fields = ('user', )


class GroupModelAdmin(
    ForceSuperuserAccess, admin.ModelAdmin
):
    list_display = ('pk', 'name', 'private', 'member_count', 'post_count')

    ordering = ('-created_at',)

    list_filter = ('private',)

    search_fields = ('name', 'id')

    inlines = (MemberTabularInline, PostTabularInline)

    date_hierarchy = 'created_at'

    raw_id_fields = ('creator',)


class PostModelAdmin(
    ForceSuperuserAccess, admin.ModelAdmin
):
    list_display = (
        'pk', 'name', 'user', 'like_count', 'group',
        'state', 'created_at', 'approved'
    )

    ordering = ('-created_at',)

    list_filter = ('state', 'approved')

    search_fields = ('attachment', 'name', 'id')

    date_hierarchy = 'created_at'

    raw_id_fields = ('user', 'group', 'namer', 'owner')


class MemberModelAdmin(
    ForceSuperuserAccess, admin.ModelAdmin
):
    list_display = ('user', 'status', 'group', 'mute', 'joined_at')

    list_filter = ('mute', 'status')

    ordering = ('-joined_at', 'mute')

    date_hierarchy = 'joined_at'

    raw_id_fields = ('user', 'group', 'creator')


class LikeModelAdmin(
    ForceSuperuserAccess, admin.ModelAdmin
):
    list_display = ('user', 'post', 'created_at')

    ordering = ('-created_at',)

    date_hierarchy = 'created_at'

    raw_id_fields = ('user', 'post')


class DeviceModelAdmin(
    ForceSuperuserAccess, admin.ModelAdmin
):
    list_display = (
        'user', 'token', 'vendor', 'locale', 'created_at', 'updated_at'
    )

    list_filter = ('vendor', 'locale')

    search_fields = ('token',)

    ordering = ('-created_at',)

    date_hierarchy = 'created_at'

    raw_id_fields = ('user',)


class ContactModelAdmin(
    ForceSuperuserAccess, admin.ModelAdmin
):
    list_display = ('pk', 'user', 'created_at')

    date_hierarchy = 'created_at'

    raw_id_fields = ('user',)


class MonkeyUserModelAdmin(
    admin.ModelAdmin
):
    list_display = ('pk', 'user')

    raw_id_fields = ('user',)


class PostCopyModelAdmin(
    admin.ModelAdmin
):
    list_display = ('parent', 'post', 'group')

    raw_id_fields = ('parent', 'post', 'group')


admin.site.register(Group, GroupModelAdmin)
admin.site.register(Code, CodeModelAdmin)
admin.site.register(Contact, ContactModelAdmin)
admin.site.register(Post, PostModelAdmin)
admin.site.register(Member, MemberModelAdmin)
admin.site.register(Like, LikeModelAdmin)
admin.site.register(Device, DeviceModelAdmin)
admin.site.register(MonkeyUser, MonkeyUserModelAdmin)
admin.site.register(PostCopy, PostCopyModelAdmin)
