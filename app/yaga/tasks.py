from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import logging

from django.core.files.storage import default_storage
from django.db import transaction
from django.utils import timezone

from app import celery

from .conf import settings
from .models import Code, Group, Post
from .providers import apns_provider

logger = logging.getLogger(__name__)


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
        ).exclude(
            attachment='',
            attachment_preview=''
        ):
            if post.attachment:
                with transaction.atomic():
                    post.attachment.delete(save=True)

            if post.attachment_preview:
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
    file_obj = 'attachment'

    def run(self, key):
        path = key.replace(settings.MEDIA_LOCATION, '')

        path = path.strip('/')

        folder, group_pk, post_pk = path.split('/')

        try:
            post = Post.objects.select_for_update().get(
                group__pk=group_pk,
                pk=post_pk
            )
        except Post.DoesNotExist:
            default_storage.delete(key)
            logging.warning('No model instance found for {key}'.format(
                key=key
            ))
        else:
            if getattr(post, self.file_obj):
                post.delete()
                logging.warning('Attempt to override {file_obj}'.format(
                    file_obj=self.file_obj
                ))
            else:
                setattr(post, self.file_obj, path)
                self.process(post)

    def process(self, post):
        if post.is_valid_attachment():
            post.checksum = post.attachment.file.key.etag.strip('"')
            post.ready = True
            post.ready_at = timezone.now()
            post.bridge.uploaded = True
            post.save(update_fields=[
                'checksum',
                'ready',
                'ready_at',
                'attachment'
            ])
        else:
            post.delete()


class PostAttachmentPreviewProcess(
    PostAttachmentProcess
):
    file_obj = 'attachment_preview'

    def process(self, post):
        if post.is_valid_attachment_preview():
            post.save(update_fields=[
                'attachment_preview'
            ])
        else:
            post.attachment_preview.delete()


class APNSPush(
    celery.Task
):
    def run(self, receivers, **kwargs):
        if receivers:
            apns_provider.push(receivers, **kwargs)
