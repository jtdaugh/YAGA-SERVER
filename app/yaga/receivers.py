from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.db import connection
from django.utils.translation import ugettext_lazy as _

from app.receivers import ModelReceiver

from .models import Device
from .tasks import APNSPush


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
    def pre_save(sender, **kwargs):
        instance = kwargs['instance']

        if instance.attachment and instance.ready and not instance.notified:
            def push_notification():
                instance.notified = True
                instance.save()

                members_tokens = Device.objects.filter(
                    vendor=Device.IOS,
                    user__in=instance.group.member_set.filter(
                        mute=False
                    ).exclude(
                        user=instance.user,
                    ).values_list('user', flat=True)
                ).values_list('token', flat=True)

                APNSPush().delay(
                    list(members_tokens),
                    alert=_('New video at group %(group_id)s!') % {
                        'group_id': instance.group.pk
                    }
                )

                user_tokens = Device.objects.filter(
                    vendor=Device.IOS,
                    user=instance.user,
                ).values_list('token', flat=True)

                APNSPush().delay(
                    list(user_tokens),
                    alert=_('Your video %(post_id)s is ready!') % {
                        'post_id': instance.pk
                    }
                )

            connection.on_commit(push_notification)
