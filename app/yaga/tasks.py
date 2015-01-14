from __future__ import absolute_import, division, unicode_literals

import datetime

from django.utils import timezone

from app import celery

from .conf import settings
from .models import Code, Group, Post


class CodeCleanup(
    celery.AtomicPeriodicTask
):
    run_every = datetime.timedelta(minutes=1)

    def run(self, *args, **kwargs):
        for code in Code.objects.filter(
            expire_at__lte=timezone.now()
        ):
            code.delete()


class GroupCleanup(
    celery.AtomicPeriodicTask
):
    run_every = datetime.timedelta(minutes=1)

    def run(self, *args, **kwargs):
        for group in Group.objects.filter(
            members=None
        ):
            keep_group = False

            for post in Post.objects.filter(
                group=group
            ):
                if post.ready:
                    post.delete()
                else:
                    keep_group = True

            if not keep_group:
                group.delete()


class PostCleanup(
    celery.AtomicPeriodicTask
):
    run_every = datetime.timedelta(minutes=1)

    def run(self, *args, **kwargs):
        expired = timezone.now() - datetime.timedelta(hours=1)

        for post in Post.objects.filter(
            created_at__lte=expired,
            ready_at=None
        ):
            post.delete()


class PostProcess(
    celery.AtomicTask
):
    def run(self, key):
        key = key.replace(settings.MEDIA_LOCATION, '')

        key = key.strip('/')

        folder, group_pk, post_pk = key.split('/')

        post = Post.objects.get(
            group__pk=group_pk,
            pk=post_pk
        )

        post.attachment = key

        post.set_meta()

        if post.mime != settings.YAGA_ALLOWED_MIME:
            post.delete()
        else:
            post.ready = True
            post.ready_at = timezone.now()
            post.save()
