from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from app.receivers import ModelReceiver

from .notifications import JoinGroupNotification


class CodeReceiver(
    ModelReceiver
):
    pass


class ContactReceiver(
    ModelReceiver
):
    pass


class DeviceReceiver(
    ModelReceiver
):
    pass


class GroupReceiver(
    ModelReceiver
):
    pass


class MonkeyUserReceiver(
    ModelReceiver
):
    pass


class MemberReceiver(
    ModelReceiver
):
    pass


class PostReceiver(
    ModelReceiver
):
    @staticmethod
    def pre_save(sender, **kwargs):
        instance = kwargs['instance']

        if not instance.pk:
            instance.group.mark_updated()


class LikeReceiver(
    ModelReceiver
):
    @staticmethod
    def pre_save(sender, **kwargs):
        instance = kwargs['instance']

        instance.post.mark_updated()

    @staticmethod
    def pre_delete(sender, **kwargs):
        instance = kwargs['instance']

        instance.post.mark_updated()


class UserReceiver(
    ModelReceiver
):
    @staticmethod
    def pre_save(sender, **kwargs):
        instance = kwargs['instance']

        if (
            instance.pk
            and instance.name
            and instance.tracker.previous('name') is None
        ):
            JoinGroupNotification.schedule(
                emitter=instance.pk
            )
