from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import logging

from django.core.files.storage import default_storage
from django.utils import timezone

from app import celery

from .conf import settings
from .models import Code, Group, Post
from .providers import apns_provider
from .storage import cloudfront_storage
from .utils import post_attachment_re

logger = logging.getLogger(__name__)


class CleanStorageTask(
    celery.Task
):
    def run(self, key, *args, **kwargs):
        full_path = key

        path = key.replace(settings.MEDIA_LOCATION, '')

        path = path.strip('/')

        try:
            default_storage.delete(path)
            cloudfront_storage.delete(full_path)
        except Exception as e:
            logger.error(e)
            raise self.retry(exc=e)


class CodeCleanupAtomicPeriodicTask(
    celery.AtomicPeriodicTask
):
    run_every = settings.YAGA_CODE_CLEANUP_RUN_EVERY

    def run(self, *args, **kwargs):
        for code in Code.objects.filter(
            expire_at__lte=timezone.now()
        ):
            code.delete()


class GroupCleanupAtomicPeriodicTask(
    celery.AtomicPeriodicTask
):
    run_every = settings.YAGA_CLEANUP_RUN_EVERY

    def run(self, *args, **kwargs):
        for group in Group.objects.filter(
            members=None
        ):
            keep_group = False

            for post in Post.atomic_objects.filter(
                group=group
            ):
                if post.ready:
                    post.delete()
                else:  # waiting for pending posts
                    keep_group = True

            if not keep_group:
                group.delete()


class PostCleanupAtomicPeriodicTask(
    celery.AtomicPeriodicTask
):
    run_every = settings.YAGA_CLEANUP_RUN_EVERY

    def run(self, *args, **kwargs):
        expired = timezone.now() - settings.YAGA_ATTACHMENT_READY_EXPIRES

        for post in Post.atomic_objects.filter(
            created_at__lte=expired,
            state=Post.state_choices.PENDING
        ):
            post.delete()


class UploadProcessTask(
    celery.Task
):
    def run(self, key, *args, **kwargs):
        if post_attachment_re.match(key):
            PostAttachmentProcessTask().delay(key)
        else:
            CleanStorageTask().delay(key)


class PostAttachmentProcessTask(
    celery.Task
):
    def run(self, key, *args, **kwargs):
        path = key.replace(settings.MEDIA_LOCATION, '')

        path = path.strip('/')

        prefix, group_pk, post_pk = path.split('/')

        try:
            post = Post.objects.get(
                group__pk=group_pk,
                pk=post_pk
            )
        except Post.DoesNotExist:
            CleanStorageTask().delay(path)

            logger.error('No model instance found for {key}'.format(
                key=key
            ))
        else:
            post.attachment = path

            if post.is_valid_attachment():
                post.checksum = post.get_checksum()

                post.mark_uploaded(
                    attachment=post.attachment.name,
                    checksum=post.checksum
                )
            else:
                post.mark_deleted()


class TranscodingTask(
    celery.Task
):
    def run(self, pk, *args, **kwargs):
        post = Post.objects.filter(
            pk=pk
        ).first()

        if post:
            if post.transcode():
                post.mark_ready(
                    attachment_preview=post.attachment_preview
                )


class APNSPushTask(
    celery.Task
):
    def run(self, receivers, *args, **kwargs):
        if receivers:
            try:
                apns_provider.push(receivers, **kwargs)
            except Exception as e:
                logger.exception(e)
                raise self.retry(exc=e)
