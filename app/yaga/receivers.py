from __future__ import absolute_import, division, unicode_literals

from django.db import connection

from app.receivers import ModelReceiver


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
