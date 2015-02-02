from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.db import connection, transaction

from app.receivers import ModelReceiver
from requestprovider import get_request

from . import utils


class MemberReceiver(
    ModelReceiver
):
    @staticmethod
    def pre_save(sender, **kwargs):
        instance = kwargs['instance']

        if not instance.pk:
            instance.group.save()

            def push_notification():
                utils.NewMemberIOSNotification(
                    member=instance
                )

            connection.on_commit(push_notification)

    @staticmethod
    def pre_delete(sender, **kwargs):
        instance = kwargs['instance']

        try:
            request = get_request()

            if request.user != instance.user:
                def push_notification():
                    utils.DeleteMemberIOSNotification(
                        member=instance,
                        deleter=request.user
                    )
            else:
                def push_notification():
                    utils.GroupLeaveIOSNotification(
                        member=instance
                    )

            connection.on_commit(push_notification)
        except Exception:
            pass


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
                    utils.NewLikeIOSNotification(
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
                utils.NewVideoIOSNotification(
                    post=instance
                )

            connection.on_commit(push_notification)
