from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import datetime

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from app import celery

from .conf import settings
from .models import Code, Group, Post
from .providers import apns_provider


class CodeCleanup(
    celery.AtomicPeriodicTask
):
    run_every = settings.YAGA_CLEANUP_RUN_EVERY

    def run(self, *args, **kwargs):
        for code in Code.objects.filter(
            expire_at__lte=timezone.now()
        ):
            code.delete()


class GroupCleanup(
    celery.AtomicPeriodicTask
):
    run_every = settings.YAGA_CLEANUP_RUN_EVERY

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
                else:  # waiting for pending posts
                    keep_group = True

            if not keep_group:
                group.delete()


class PostCleanup(
    celery.AtomicPeriodicTask
):
    run_every = settings.YAGA_CLEANUP_RUN_EVERY

    def run(self, *args, **kwargs):
        expired = timezone.now() - settings.YAGA_ATTACHMENT_READY_EXPIRES

        for post in Post.objects.filter(
            created_at__lte=expired,
            ready=False
        ):
            post.delete()


class DeletedPostCleanup(
    celery.PeriodicTask
):
    run_every = settings.YAGA_CLEANUP_RUN_EVERY

    def run(self, *args, **kwargs):
        for post in Post.objects.filter(
            deleted=True
        ).filter(
            Q(attachment__isnull=False)
            |
            Q(attachment_preview__isnull=False)
        ):
            if post.attachment is not None:
                with transaction.atomic():
                    post.attachment.delete(save=True)

            if post.attachment_preview is not None:
                with transaction.atomic():
                    post.attachment_preview.delete(save=True)


class UploadProcess(
    celery.Task
):
    def run(self, key):
        if settings.YAGA_ATTACHMENT_PREVIEW_PREFIX in key:
            PostAttachmentPreviewProcess().delay(key)
        elif settings.YAGA_ATTACHMENT_PREFIX in key:
            PostAttachmentProcess().delay(key)


class PostAttachmentProcess(
    celery.AtomicTask
):
    def setup_post(self, key):
        key = key.replace(settings.MEDIA_LOCATION, '')

        key = key.strip('/')

        folder, group_pk, post_pk = key.split('/')

        post = Post.objects.get(
            group__pk=group_pk,
            pk=post_pk
        )

        self.post = post
        self.key = key

    def run(self, key):
        self.setup_post(key)

        self.post.attachment = self.key

        if self.post.is_valid_attachment():
            self.post.checksum = self.post.attachment.file.key.etag.strip('"')
            self.post.ready = True
            self.post.ready_at = timezone.now()
            self.post.bridge.uploaded = True
            self.post.save()
        else:
            self.post.delete()


class PostAttachmentPreviewProcess(
    PostAttachmentProcess
):
    def run(self, key):
        self.setup_post(key)

        self.post.attachment_preview = self.key

        if self.post.is_valid_attachment_preview():
            self.post.save()
        else:
            self.post.attachment_preview.delete()


class APNSPush(
    celery.Task
):
    def run(self, receivers, **kwargs):
        if receivers:
            apns_provider.push(receivers, **kwargs)
