from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.db import connection, transaction
from django.utils.translation import ugettext_lazy as _

from app.receivers import ModelReceiver

from .models import Device
from .tasks import APNSPush


class MemberReceiver(
    ModelReceiver
):
    @staticmethod
    def pre_save(sender, **kwargs):
        instance = kwargs['instance']

        if not instance.pk:
            instance.group.save()


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

        if instance.attachment and instance.ready and not instance.notified:
            instance.notified = True

            def push_notification():
                members_tokens = Device.objects.filter(
                    vendor=Device.IOS,
                    user__in=instance.group.member_set.filter(
                        mute=False
                    ).exclude(
                        user=instance.user,
                    ).values_list('user', flat=True)
                ).values_list('token', flat=True)

                members_tokens = list(members_tokens)

                if members_tokens:
                    APNSPush().delay(
                        members_tokens,
                        alert=_('New video at group %(group_id)s!') % {
                            'group_id': instance.group.pk
                        }
                    )

                user_tokens = Device.objects.filter(
                    vendor=Device.IOS,
                    user=instance.user,
                ).values_list('token', flat=True)

                user_tokens = list(user_tokens)

                if user_tokens:
                    APNSPush().delay(
                        user_tokens,
                        alert=_('Your video %(post_id)s is ready!') % {
                            'post_id': instance.pk
                        }
                    )

            connection.on_commit(push_notification)
