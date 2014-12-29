from __future__ import absolute_import, division, unicode_literals

from app.receivers import ModelReceiver


class PostReceiver(ModelReceiver):
    @staticmethod
    def post_delete(sender, **kwargs):
        instance = kwargs['instance']

        instance.attachment.delete(save=False)
