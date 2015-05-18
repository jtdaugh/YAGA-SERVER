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
from .utils import post_attachment_re

logger = logging.getLogger(__name__)


class CleanStorageTask(
    celery.Task
):
    def run(self, key, *args, **kwargs):
        path = key.replace(settings.MEDIA_LOCATION, '')

        path = path.strip('/')

        try:
            default_storage.delete(path)
        except Exception as e:

            self.retry(key, *args, exc=e, **kwargs)

            logger.error(e)


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
        try:
            if post_attachment_re.match(key):
                PostAttachmentValidateTask.delay(key)
            else:
                CleanStorageTask().delay(key)
        except Exception as e:
            self.retry(key, *args, exc=e, **kwargs)

            logger.exception(e)


class PostAttachmentValidateTask(
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
            if post.attachment:
                post.mark_deleted()

                logger.error('Attempt to override {file_obj}'.format(
                    file_obj=post.attachment.name
                ))
            else:
                post.attachment = path

                if post.is_valid_attachment():
                    post.checksum = post.get_checksum()

                    if Post.objects.filter(
                        group=post.group,
                        checksum=post.checksum
                    ).exists():
                        post.atomic_delete()

                        logger.error('Dropped duplicate {file_obj}'.format(
                            file_obj=post.attachment.name
                        ))
                    else:
                        post.mark_uploaded()
                else:
                    post.atomic_delete()


class APNSPushTask(
    celery.Task
):
    def run(self, receivers, *args, **kwargs):
        if receivers:
            try:
                apns_provider.push(receivers, **kwargs)
            except Exception as e:

                self.retry(receivers, *args, exc=e, **kwargs)

                logger.exception(e)
