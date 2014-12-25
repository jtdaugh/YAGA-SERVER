from __future__ import absolute_import, division, unicode_literals

from app.receivers import ModelReceiver

from .models import Post


class PostReceiver(ModelReceiver):
    @staticmethod
    def post_delete(sender, **kwargs):
        instance = kwargs['instance']

        instance.attachment.delete(save=False)


class MemberReceiver(ModelReceiver):
    @staticmethod
    def post_delete(sender, **kwargs):
        instance = kwargs['instance']

        for post in Post.objects.filter(
            group=instance.group,
            user=instance.user
        ):
            post.delete()
