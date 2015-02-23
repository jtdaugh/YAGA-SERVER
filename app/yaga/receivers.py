from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.db import connection, transaction

from app.receivers import ModelReceiver
from requestprovider import get_request

from . import providers


class MemberReceiver(
    ModelReceiver
):
    @staticmethod
    def pre_save(sender, **kwargs):
        instance = kwargs['instance']

        if not instance.pk:
            instance.group.save()

            def push_notification():
                providers.NewMemberIOSNotification(
                    member=instance
                )

            connection.on_commit(push_notification)

    @staticmethod
    def pre_delete(sender, **kwargs):
        instance = kwargs['instance']

        if hasattr(instance.bridge, 'deleter'):
            user = instance.bridge.deleter
        else:
            user = get_request().user

        if user != instance.user:
            def push_notification():
                providers.DeleteMemberIOSNotification(
                    member=instance,
                    deleter=user
                )
        else:
            def push_notification():
                providers.GroupLeaveIOSNotification(
                    member=instance
                )

        connection.on_commit(push_notification)


class LikeReceiver(
    ModelReceiver
):
    @staticmethod
    def pre_save(sender, **kwargs):
        instance = kwargs['instance']

        if not instance.pk:
            instance.post.save()

            if instance.post.user != instance.user:
                def push_notification():
                    providers.NewLikeIOSNotification(
                        like=instance
                    )

                connection.on_commit(push_notification)


class PostReceiver(
    ModelReceiver
):
    @staticmethod
    def post_delete(sender, **kwargs):
        instance = kwargs['instance']

        if instance.attachment:
            def delete_attachment():
                instance.attachment.delete(save=False)

            connection.on_commit(delete_attachment)

    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs['instance']

        if instance.deleted and instance.attachment:
            def delete_attachment():
                with transaction.atomic():
                    instance.attachment.delete()

            connection.on_commit(delete_attachment)

    @staticmethod
    def pre_save(sender, **kwargs):
        instance = kwargs['instance']

        instance.group.save()

        if hasattr(instance.bridge, 'uploaded'):
            def push_notification():
                providers.NewVideoIOSNotification(
                    post=instance
                )

            connection.on_commit(push_notification)
