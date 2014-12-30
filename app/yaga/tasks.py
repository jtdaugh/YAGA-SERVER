from __future__ import absolute_import, division, unicode_literals

import datetime

from django.utils import timezone
from django.conf import settings

from app import celery
from .models import Code, Group, Post


class CodeCleanup(celery.PeriodicTask):
    run_every = datetime.timedelta(minutes=1)

    def run(self, *args, **kwargs):
        Code.objects.filter(
            expire_at__lte=timezone.now()
        ).delete()


class GroupCleanup(celery.PeriodicTask):
    run_every = datetime.timedelta(minutes=1)

    def run(self, *args, **kwargs):
        for group in Group.objects.filter(
            members=None
        ):
            group.delete()


class PostCleanup(celery.PeriodicTask):
    run_every = datetime.timedelta(minutes=1)

    def run(self, *args, **kwargs):
        expired = timezone.now() - datetime.timedelta(hours=1)

        for post in Post.objects.filter(
            created_at__lte=expired,
            ready_at=None
        ):
            post.delete()


class PostProcess(celery.Task):
    def run(self, key):
        key = key.replace(settings.MEDIA_LOCATION, '')
        key = key.strip('/')

        group_pk, post_pk = key.split('/')

        post = Post.objects.get(
            group__pk=group_pk,
            pk=post_pk
        )

        post.attachment = key
        post.set_meta()
        post.ready = True
        post.ready_at = timezone.now()
        post.save()
