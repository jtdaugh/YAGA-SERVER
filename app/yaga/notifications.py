from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib.auth import get_user_model
from django.db import connection
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import override

from .conf import settings
from .models import Device, Group, Like, Member, Post
from .providers import apns_provider


# from django.utils.lru_cache import lru_cache
# , ungettext
# Contact,


class NotificationInstances(
    type
):
    _instances = {}

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
    def __init__(self):
        self.kwargs = None
        self._object = None

    @classmethod
    def schedule(cls, **kwargs):
        def _schedule():
            NotificationTask().delay(
                cls.__name__, **kwargs
            )

        connection.on_commit(_schedule)

    @classmethod
    def notify(cls, **kwargs):
        instance = cls()

        instance.kwargs = kwargs

        instance.send()

    def check_condition(self):
        return True

    def check_threshold(self):
        return True

    @property
    def object(self):
        if self._object is None:
            self._object = self.get_object()

        return self._object

    def get_meta(self):
        return {}

    def get_object(self):
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

    def get_ios_push_kwargs(self):
        return {
            'badge': settings.YAGA_PUSH_BADGE,
            'sound': settings.YAGA_PUSH_SOUND,
            'meta': self.get_meta(),
            'alert': self.format_message()
        }

    def get_android_notification_kwargs(self):
        raise NotImplementedError

    def send(self):
        if self.check_condition() and self.check_threshold():
            token_map = self.get_token_map(
                self.get_devices(
                    self.get_receivers()
                )
            )

            for code, title in settings.LANGUAGES:
                with override(code.lower()):
                    apns_provider.schedule(
                        token_map[
                            Device.vendor_choices.IOS
                        ][code.lower()],
                        **self.get_ios_push_kwargs()
                    )

                    # gcm_provider.schedule(
                    #     token_map[
                    #         Device.vendor_choices.ANDROID
                    #     ][code.lower()],
                    #     **self.get_android_notification_kwargs()
                    # )


class DirectNotification(
    Notification
):
    def get_target(self):
        raise NotImplementedError

    def get_receivers(self):
        return [self.get_target()]


class GroupNotification(
    Notification
):
    def get_group(self):
        raise NotImplementedError

    def get_emitter(self):
        raise NotImplementedError

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
    def get_object(self):
        return Post.objects.get(
            pk=self.kwargs['post']
        )

    def get_meta(self):
        return {
            'event': 'post',
            'group_id': str(self.object.group.pk)
        }

    def get_group(self):
        return self.object.group

    def get_emitter(self):
        return self.object.user

    def get_message(self):
        return _('{user} posted into {group}')

    def get_message_kwargs(self):
        return {
            'group': self.get_group().name,
            'user': self.get_emitter().get_username()
        }


class InviteDirectNotification(
    DirectNotification
):
    def get_object(self):
        return Member.objects.get(
            pk=self.kwargs['member']
        )

    def get_meta(self):
        return {
            'event': 'invite',
            'group_id': str(self.object.group.pk)
        }

    def get_target(self):
        return self.object.user

    def get_message_kwargs(self):
        return {
            'group': self.object.group.name,
            'emitter': self.object.creator.get_username()
        }

    def get_message(self):
        return _('{emitter} has added you to {group}')


class LikeDirectNotification(
    DirectNotification
):
    def get_object(self):
        return Like.objects.get(
            pk=self.kwargs['like']
        )

    def get_meta(self):
        return {
            'event': 'like',
            'post_id': str(self.object.post.pk),
            'group_id': str(self.object.post.group.pk),
        }

    def get_target(self):
        return self.object.post.user

    def get_message_kwargs(self):
        return {
            'user': self.object.user.get_username(),
            'group': self.object.post.group.name,
        }

    def get_message(self):
        return _('{user} liked your video in {group}')


class LeftGroupNotification(
    GroupNotification
):
    def get_object(self):
        class Object(
            object
        ):
            def __init__(self, this):
                self.user = get_user_model().objects.get(
                    pk=this.kwargs['user']
                )

                self.group = Group.objects.get(
                    pk=this.kwargs['group']
                )

        return Object(self)

    def get_meta(self):
        return {
            'event': 'leave',
            'user_id': str(self.object.user.pk),
            'group_id': str(self.object.group.pk),
        }

    def get_group(self):
        return self.object.group

    def get_emitter(self):
        return self.object.user

    def get_message_kwargs(self):
        return {
            'group': self.object.group.name,
            'member': self.object.user.get_username(),
        }

    def get_message(self):
        return _('{member} has left {group}')


class KickGroupNotification(
    GroupNotification
):
    def get_object(self):
        class Object(
            object
        ):
            def __init__(self, this):
                self.user = get_user_model().objects.get(
                    pk=this.kwargs['user']
                )

                self.group = Group.objects.get(
                    pk=this.kwargs['group']
                )

                self.emitter = get_user_model().objects.get(
                    pk=this.kwargs['emitter']
                )

        return Object(self)

    def get_meta(self):
        return {
            'event': 'kick',
            'user_id': str(self.object.user.pk),
            'group_id': str(self.object.group.pk),
        }

    def get_group(self):
        return self.object.group

    def get_emitter(self):
        return self.object.emitter

    def get_message_kwargs(self):
        return {
            'group': self.object.group.name,
            'member': self.object.user.get_username(),
            'emitter': self.object.emitter.get_username()
        }

    def get_message(self):
        return _('{emitter} removed {member} from {group}')


class KickDirectNotification(
    DirectNotification
):
    def get_object(self):
        class Object(
            object
        ):
            def __init__(self, this):
                self.user = get_user_model().objects.get(
                    pk=this.kwargs['user']
                )

                self.group = Group.objects.get(
                    pk=this.kwargs['group']
                )

                self.emitter = get_user_model().objects.get(
                    pk=this.kwargs['emitter']
                )

        return Object(self)

    def get_meta(self):
        return {
            'event': 'kick',
            'user_id': str(self.object.user.pk),
            'group_id': str(self.object.group.pk),
        }

    def get_target(self):
        return self.object.user

    def get_message_kwargs(self):
        return {
            'group': self.object.group.name,
            'member': self.object.user.get_username(),
            'emitter': self.object.emitter.get_username()
        }

    def get_message(self):
        return _('{emitter} has removed you from {group}')


class CaptionDirectNotification(
    DirectNotification
):
    def get_object(self):
        return Post.objects.get(
            pk=self.kwargs['post']
        )

    def get_meta(self):
        return {
            'event': 'caption',
            'post_id': str(self.object.pk),
            'group_id': str(self.object.group.pk),
        }

    def get_target(self):
        return self.object.user

    def get_message_kwargs(self):
        return {
            'user': self.object.namer.get_username(),
            'group': self.object.group.name,
        }

    def get_message(self):
        return _('{user} captioned your video in {group}')


class RenameGroupNotification(
    GroupNotification
):
    def get_object(self):
        class Object(
            object
        ):
            def __init__(self, this):
                self.group = Group.objects.get(
                    pk=this.kwargs['group']
                )

                self.emitter = get_user_model().objects.get(
                    pk=this.kwargs['emitter']
                )

                self.old_name = this.kwargs['old_name']

        return Object(self)

    def get_group(self):
        return self.object.group

    def get_meta(self):
        return {
            'event': 'rename',
            'group_id': str(self.object.group.pk),
        }

    def get_emitter(self):
        return self.object.emitter

    def get_message_kwargs(self):
        return {
            'emitter': self.object.emitter.get_username(),
            'old_name': self.object.old_name,
            'new_name': self.object.group.name
        }

    def get_message(self):
        return _('{emitter} renamed {old_name} to {new_name}')


# class NewMembersBatchIOSNotification(
#     NewMemberIOSNotification
# ):
#     BROADCAST = True
#     TARGET = False

#     def get_meta(self):
#         return {
#             'event': 'members',
#             'group_id': str(self.group.pk)
#         }

#     def get_group(self):
#         return self.group

#     def get_emitter(self):
#         return self.creator

#     def get_targets(self):
#         return [member.user for member in self.members]

#     def get_broadcast_exclude(self):
#         return {
#             'user__in': list(set([
#                 self.get_emitter()
#             ] + self.get_targets()))
#         }

#     def get_broadcast_kwargs(self):
#         return {
#             'group': self.group.name,
#             'targets': self.get_new_members(),
#             'creator': self.creator.get_username()
#         }

#     def map_members(self, members):
#         return [
#             member.user.get_username() for member in members
#         ]

#     def get_new_members(self):
#         if not self.group.bridge.new_members:
#             self.SKIP = True
#             return ''
#         elif len(self.group.bridge.new_members) == 1:
#             return self.group.bridge.new_members.pop().user.get_username()
#         elif (
#             settings.YAGA_PUSH_NEW_MEMBERS_BATCH_LIMIT
#             >=
#             len(self.group.bridge.new_members)
#         ):
#             users = self.map_members(self.group.bridge.new_members)

#             return _('{list} and {last}').format(
#                 list=', '.join(users[:-1]),
#                 last=users[-1]
#             )
#         else:
#             member_list = self.group.bridge.new_members[
#                 :settings.YAGA_PUSH_NEW_MEMBERS_BATCH_LIMIT - 1
#             ]

#             users = self.map_members(member_list)

#             count = (
#                 len(self.group.bridge.new_members)
#                 -
#                 settings.YAGA_PUSH_NEW_MEMBERS_BATCH_LIMIT
#             ) + 1

#             return ungettext(
#                 '{list} and {count} other',
#                 '{list} and {count} others',
#                 count
#             ).format(
#                 list=', '.join(users),
#                 count=count
#             )

#     def get_broadcast_message(self):
#         return _('{creator} added {targets} to {group}')


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
