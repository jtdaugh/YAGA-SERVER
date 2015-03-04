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

            if instance.user.name is not None:
                if len(instance.group.bridge.new_members) == 0:
                    def push_notification():
                        providers.NewMembersBatchIOSNotification(
                            group=instance.group,
                            creator=instance.creator
                        )

                    connection.on_commit(push_notification)

                instance.group.bridge.new_members.append(instance)

                def push_notification():
                    providers.NewMemberIOSNotification(
                        member=instance
                    )

                connection.on_commit(push_notification)

    @staticmethod
    def pre_delete(sender, **kwargs):
        instance = kwargs['instance']

        instance.group.save()

        if hasattr(instance.bridge, 'deleter'):
            user = instance.bridge.deleter
        else:
            user = get_request().user

        if instance.user.name is not None:
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

        if instance.pk is not None:
            if instance.tracker.previous('name') != instance.name:
                if hasattr(instance.bridge, 'updater'):
                    if instance.bridge.updater != instance.user:
                        def push_notification():
                            providers.NewCaptionIOSNotification(
                                post=instance
                            )

                        connection.on_commit(push_notification)


class UserReceiver(
    ModelReceiver
):
    @staticmethod
    def pre_save(sender, **kwargs):
        instance = kwargs['instance']

        if (
            instance.tracker.previous('name') is None
            and
            instance.name is not None
        ):
            def push_notification():
                providers.NewUserIOSNotification(
                    user=instance
                )

            connection.on_commit(push_notification)


class GroupReceiver(
    ModelReceiver
):
    @staticmethod
    def post_init(sender, **kwargs):
        instance = kwargs['instance']

        instance.bridge.new_members = []
