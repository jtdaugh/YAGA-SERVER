from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import override

from .models import Device
from .tasks import APNSPush


class IOSNotification(
    object
):
    VENDOR = Device.IOS
    BROADCAST = False
    TARGET = False

    def __init__(self, **kwargs):
        for key, value in list(kwargs.items()):
            setattr(self, key, value)

        self.push()

    def get_broadcast_message(self):
        return ''

    def get_broadcast_kwargs(self):
        return {}

    def get_target_message(self):
        return ''

    def get_target_kwargs(self):
        return {}

    def get_group(self):
        return self.group

    def get_emitter(self):
        return self.user

    def get_broadcast_receivers(self):
        return self.get_group().member_set.filter(
            mute=False
        ).values_list('user', flat=True)

        # .exclude(
        #     user=self.get_emitter()
        # )

    def get_target_receivers(self):
        return [self.get_emitter()]

    def get_devices(self, users):
        devices = Device.objects.filter(
            vendor=self.VENDOR,
            user__in=users
        )

        return devices

    def get_token_map(self, devices):
        token_map = {}

        for device in devices:
            if token_map.get(device.locale) is None:
                token_map[device.locale] = []

            token_map[device.locale].append(device.token)

        return token_map

    def push_broadcast(self):
        devices = self.get_devices(self.get_broadcast_receivers())

        token_map = self.get_token_map(devices)

        if token_map:
            for locale, tokens in list(token_map.items()):
                with override(locale):
                    APNSPush().delay(
                        tokens,
                        alert=self.get_broadcast_message().format(
                            **self.get_broadcast_kwargs()
                        )
                    )

    def push_target(self):
        devices = self.get_devices(self.get_target_receivers())

        token_map = self.get_token_map(devices)

        if token_map:
            for locale, tokens in list(token_map.items()):
                with override(locale):
                    APNSPush().delay(
                        tokens,
                        alert=self.get_target_message().format(
                            **self.get_target_kwargs()
                        )
                    )

    def push(self):
        if self.TARGET:
            self.push_target()

        if self.BROADCAST:
            self.push_broadcast()


class NewVideoIOSNotification(
    IOSNotification
):
    BROADCAST = True

    def get_group(self):
        return self.post.group

    def get_emitter(self):
        return self.post.user

    def get_broadcast_message(self):
        return _('{user} posted into {group}')

    def get_broadcast_kwargs(self):
        return {
            'group': self.get_group().name,
            'user': self.get_emitter()
        }


class NewMemberIOSNotification(
    IOSNotification
):
    BROADCAST = True
    TARGET = True

    def get_group(self):
        return self.member.group

    def get_emitter(self):
        return self.member.user

    def get_broadcast_message(self):
        return _('{creator} added {member} to {group}')

    def get_broadcast_kwargs(self):
        return {
            'group': self.member.group.name,
            'member': self.member.user.get_username(),
            'creator': self.member.creator.get_username()
        }

    def get_target_message(self):
        return _('{creator} has added you to {group}')

    def get_target_kwargs(self):
        return self.get_broadcast_kwargs()


class NewLikeIOSNotification(
    IOSNotification
):
    TARGET = True

    def get_emitter(self):
        return self.like.user

    def get_target_message(self):
        return _('{user} liked your video in {group}')

    def get_target_kwargs(self):
        return {
            'user': self.like.post.user.get_username(),
            'group': self.like.post.group.name,
        }


class DeleteMemberIOSNotification(
    IOSNotification
):
    BROADCAST = True
    TARGET = True

    def get_group(self):
        return self.member.group

    def get_emitter(self):
        return self.member.user

    def get_broadcast_message(self):
        return _('{deleter} removed {member} from {group}')

    def get_broadcast_kwargs(self):
        return {
            'group': self.member.group.name,
            'member': self.member.user.get_username(),
            'deleter': self.deleter
        }

    def get_target_message(self):
        return _('{creator} has removed you from {group}')

    def get_target_kwargs(self):
        return self.get_broadcast_kwargs()


class GroupLeaveIOSNotification(
    IOSNotification
):
    BROADCAST = True

    def get_group(self):
        return self.member.group

    def get_emitter(self):
        return self.member.user

    def get_broadcast_message(self):
        return _('{member} has left {group}')

    def get_broadcast_kwargs(self):
        return {
            'group': self.member.group.name,
            'member': self.member.user.get_username(),
        }
