from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib.auth import get_user_model
from django.db import connection
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import override, ungettext
from django.utils.lru_cache import lru_cache

from .conf import settings
from .models import Device, Group, Post
from .providers import apns_provider


class NotificationInstances(
    type
):
    _instances = {}

    @classmethod
    def get_instance(cls, instance):
        return cls._instances[instance]

    def __new__(cls, name, parents, dct):
        instance = super(NotificationInstances, cls).__new__(
            cls, name, parents, dct
        )

        if name not in cls._instances:
            cls._instances[name] = instance

        return instance


class Notification(
    six.with_metaclass(NotificationInstances, object)
):
    def __init__(self, **kwargs):
        raise NotImplementedError

    @classmethod
    def schedule(cls, **kwargs):
        def _schedule():
            NotificationTask().delay(
                cls.__name__, **kwargs
            )

        connection.on_commit(_schedule)

    def load_post(self, pk):
        return Post.objects.select_related(
            'user',
            'group'
        ).get(
            pk=pk
        )

    def load_group(self, pk):
        return Group.objects.get(
            pk=pk
        )

    def load_user(self, pk):
        return get_user_model().objects.get(
            pk=pk
        )

    @lru_cache()
    def get_post(self):
        return self.post

    @lru_cache()
    def get_group(self):
        return self.group

    @lru_cache()
    def get_target(self):
        return self.target

    @lru_cache()
    def get_emitter(self):
        return self.emitter

    def check_condition(self):
        return True

    def check_threshold(self):
        return True

    def get_meta(self):
        raise NotImplementedError

    def get_message(self):
        raise NotImplementedError

    def get_message_kwargs(self):
        raise NotImplementedError

    def get_devices(self, users):
        devices = Device.objects.filter(
            user__in=users
        )

        return devices

    def get_token_map(self, devices):
        token_map = {
            Device.vendor_choices.IOS: {},
            Device.vendor_choices.ANDROID: {}
        }

        for code, title in settings.LANGUAGES:
            token_map[Device.vendor_choices.IOS][code.lower()] = []
            token_map[Device.vendor_choices.ANDROID][code.lower()] = []

        for device in devices:
            token_map[device.vendor][device.locale.lower()].append(
                device.token
            )

        return token_map

    def format_message(self):
        return self.get_message().format(
            **self.get_message_kwargs()
        )

    def get_ios_push(self):
        return {
            'badge': settings.YAGA_PUSH_BADGE,
            'sound': settings.YAGA_PUSH_SOUND,
            'meta': self.get_meta(),
            'alert': self.format_message()
        }

    def get_android_message(self):
        raise NotImplementedError

    def notify(self):
        if self.check_condition() and self.check_threshold():
            token_map = self.get_token_map(
                self.get_devices(
                    self.get_receivers()
                )
            )

            for code, title in settings.LANGUAGES:
                with override(code.lower()):
                    ios_receivers = token_map[
                        Device.vendor_choices.IOS
                    ][code.lower()]

                    if ios_receivers:
                        apns_provider.schedule(
                            ios_receivers,
                            **self.get_ios_push()
                        )

                    # android_receivers = token_map[
                    #     Device.vendor_choices.ANDROID
                    # ][code.lower()]

                    # if android_receivers:
                    #     gcm_provider.schedule(
                    #         android_receivers,
                    #         **self.get_android_notification_kwargs()
                    #     )


class DirectNotification(
    Notification
):
    def get_receivers(self):
        return [self.get_target()]


class GroupNotification(
    Notification
):
    def get_exclude(self):
        return {
            'user': self.get_emitter()
        }

    def get_receivers(self):
        members = self.get_group().member_set.select_related(
            'user'
        ).filter(
            mute=False
        ).exclude(
            **self.get_exclude()
        )

        return [member.user for member in members]


class PostGroupNotification(
    GroupNotification
):
    def __init__(self, **kwargs):
        self.post = self.load_post(kwargs['post'])
        self.group = self.post.group
        self.emitter = self.post.user

    def get_meta(self):
        return {
            'event': 'post',
            'post_id': str(self.get_post().pk),
            'group_id': str(self.get_group().pk)
        }

    def get_message(self):
        return _('{emitter} posted into {group}')

    def get_message_kwargs(self):
        return {
            'group': self.get_group().name,
            'emitter': self.get_emitter().get_username()
        }


class InviteDirectNotification(
    DirectNotification
):
    def __init__(self, **kwargs):
        self.group = self.load_group(kwargs['group'])
        self.target = self.load_user(kwargs['target'])
        self.emitter = self.load_user(kwargs['emitter'])

    def get_meta(self):
        return {
            'event': 'invite',
            'group_id': str(self.get_group().pk)
        }

    def get_message_kwargs(self):
        return {
            'group': self.get_group().name,
            'emitter': self.get_emitter().get_username()
        }

    def get_message(self):
        return _('{emitter} has added you to {group}')


class LikeDirectNotification(
    DirectNotification
):
    def check_condition(self):
        return self.get_target() != self.get_emitter()

    def __init__(self, **kwargs):
        self.post = self.load_post(kwargs['post'])
        self.group = self.post.group
        self.target = self.post.user
        self.emitter = self.load_user(kwargs['emitter'])

    def get_meta(self):
        return {
            'event': 'like',
            'post_id': str(self.get_post().pk),
            'group_id': str(self.get_group().pk),
        }

    def get_message_kwargs(self):
        return {
            'emitter': self.get_emitter().get_username(),
            'group': self.get_group().name,
        }

    def get_message(self):
        return _('{emitter} liked your video in {group}')


class LeftGroupNotification(
    GroupNotification
):
    def __init__(self, **kwargs):
        self.group = self.load_group(kwargs['group'])
        self.emitter = self.load_user(kwargs['emitter'])

    def get_meta(self):
        return {
            'event': 'leave',
            'user_id': str(self.get_emitter().pk),
            'group_id': str(self.get_group().pk),
        }

    def get_message_kwargs(self):
        return {
            'group': self.get_group().name,
            'emitter': self.get_emitter().get_username(),
        }

    def get_message(self):
        return _('{emitter} has left {group}')


class KickGroupNotification(
    GroupNotification
):
    def check_condition(self):
        return self.get_target().name is not None

    def __init__(self, **kwargs):
        self.group = self.load_group(kwargs['group'])
        self.target = self.load_user(kwargs['target'])
        self.emitter = self.load_user(kwargs['emitter'])

    def get_meta(self):
        return {
            'event': 'kick',
            'user_id': str(self.get_target().pk),
            'group_id': str(self.get_group().pk),
        }

    def get_message_kwargs(self):
        return {
            'group': self.get_group().name,
            'target': self.get_target().get_username(),
            'emitter': self.get_emitter().get_username()
        }

    def get_message(self):
        return _('{emitter} removed {target} from {group}')


class KickDirectNotification(
    DirectNotification
):
    def __init__(self, **kwargs):
        self.group = self.load_group(kwargs['group'])
        self.target = self.load_user(kwargs['target'])
        self.emitter = self.load_user(kwargs['emitter'])

    def get_meta(self):
        return {
            'event': 'kick',
            'user_id': str(self.get_target().pk),
            'group_id': str(self.get_group().pk),
        }

    def get_message_kwargs(self):
        return {
            'group': self.get_group().name,
            'emitter': self.get_emitter().get_username()
        }

    def get_message(self):
        return _('{emitter} has removed you from {group}')


class CaptionDirectNotification(
    DirectNotification
):
    def check_condition(self):
        return self.group.member_set.filter(
            user=self.target
        ).first() is not None

    def __init__(self, **kwargs):
        self.post = self.load_post(kwargs['post'])
        self.group = self.post.group
        self.target = self.post.user
        self.emitter = self.load_user(kwargs['emitter'])

    def get_meta(self):
        return {
            'event': 'caption',
            'post_id': str(self.get_post().pk),
            'group_id': str(self.get_group().pk),
        }

    def get_message_kwargs(self):
        return {
            'group': self.get_group().name,
            'emitter': self.get_target().get_username()
        }

    def get_message(self):
        return _('{emitter} captioned your video in {group}')


class RenameGroupNotification(
    GroupNotification
):
    def __init__(self, **kwargs):
        self.group = self.load_group(kwargs['group'])
        self.emitter = self.load_user(kwargs['emitter'])

        self.old_name = kwargs['old_name']
        self.new_name = kwargs['new_name']

    def get_meta(self):
        return {
            'event': 'rename',
            'group_id': str(self.get_group().pk),
        }

    def get_message_kwargs(self):
        return {
            'emitter': self.get_emitter().get_username(),
            'old_name': self.old_name,
            'new_name': self.new_name
        }

    def get_message(self):
        return _('{emitter} renamed {old_name} to {new_name}')


class MembersGroupNotification(
    GroupNotification
):
    def check_condition(self):
        return bool(self.get_targets())

    def __init__(self, **kwargs):
        self.group = self.load_group(kwargs['group'])
        self.targets = self.load_users(kwargs['targets'])
        self.emitter = self.load_user(kwargs['emitter'])

    def load_users(self, pks):
        return get_user_model().objects.filter(
            pk__in=pks
        ).exclude(
            name=None
        )

    @lru_cache()
    def get_targets(self):
        return list(self.targets)

    def get_usernames(self, users):
        return [user.get_username() for user in users]

    def get_targets_string(self):
        if len(self.get_targets()) == 1:
            return self.get_targets()[0].get_username()
        elif (
            settings.YAGA_PUSH_NEW_MEMBERS_LIMIT
            >=
            len(self.get_targets())
        ):
            users = self.get_usernames(self.get_targets())

            return _('{list} and {last}').format(
                list=', '.join(users[:-1]),
                last=users[-1]
            )
        else:
            users = self.get_usernames(
                self.get_targets()[:settings.YAGA_PUSH_NEW_MEMBERS_LIMIT - 1]
            )

            count = (
                len(self.get_targets())
                -
                settings.YAGA_PUSH_NEW_MEMBERS_LIMIT
            ) + 1

            return ungettext(
                '{list} and {count} other',
                '{list} and {count} others',
                count
            ).format(
                list=', '.join(users),
                count=count
            )

    def get_exclude(self):
        return {
            'user__in': list(set(
                [self.get_emitter()] + self.get_targets()
            ))
        }

    def get_meta(self):
        return {
            'event': 'members',
            'group_id': str(self.get_group().pk)
        }

    def get_message_kwargs(self):
        return {
            'group': self.get_group().name,
            'targets': self.get_targets_string(),
            'emitter': self.get_emitter().get_username()
        }

    def get_message(self):
        return _('{emitter} added {targets} to {group}')


# class NewUserIOSNotification(
#     IOSNotification
# ):
#     @lru_cache()
#     def get_groups(self):
#         return [member.group for member in Member.objects.filter(
#             user=self.user
#         )]

#     def get_emitter(self):
#         return self.user

#     def push(self):
#         self.push_broadcast_groups()

#         self.push_broadcast_contacts()

#     def push_broadcast_groups(self):
#         groups = self.get_groups()

#         self.get_broadcast_message = lambda: _('{member} joined {group}')

#         for group in groups:
#             self.get_meta = lambda: {
#                 'event': 'join',
#                 'user_id': str(self.user.pk),
#                 'group_id': str(group.pk),
#             }

#             self.get_broadcast_kwargs = lambda: {
#                 'member': self.user.get_username(),
#                 'group': group.name
#             }

#             self.get_group = lambda: group

#             self.push_broadcast()

#     def push_broadcast_contacts(self):
#         users = [member.user for member in Member.objects.filter(
#             group__in=self.get_groups()
#         ).distinct('user')]

#         self.get_broadcast_receivers = lambda: [
#             contact.user for contact in Contact.objects.filter(
#                 phones__contains=[self.user.phone.as_e164],
#             ).exclude(
#                 user__in=users
#             )
#         ]

#         self.get_meta = lambda: {
#             'event': 'registration',
#             'user_id': str(self.user.pk)
#         }

#         self.get_broadcast_message = lambda: _('{member} joined Yaga')

#         self.get_broadcast_kwargs = lambda: {
#             'member': self.user.get_username()
#         }

#         self.push_broadcast()
from .tasks import NotificationTask  # noqa # isort:skip
