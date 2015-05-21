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


if settings.YAGA_PERIODIC_CLEANUP:
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

        def run(self):
            for group in Group.objects.filter(
                members=None
            ):
                keep_group = False

                for post in Post.atomic_objects.filter(
                    group=group
                ):
                    if post.state in [
                        Post.state_choices.READY,
                        Post.state_choices.DELETED
                    ]:
                        post.delete()
                    else:  # waiting for pending posts
                        keep_group = True

                if not keep_group:
                    group.delete()

    class PostCleanupAtomicPeriodicTask(
        celery.AtomicPeriodicTask
    ):
        run_every = settings.YAGA_CLEANUP_RUN_EVERY

        def run(self):
            expired = timezone.now() - settings.YAGA_ATTACHMENT_READY_EXPIRES

            for post in Post.atomic_objects.filter(
                created_at__lte=expired,
                state=Post.state_choices.PENDING
            ):
                post.delete()

    class APNSFeedBackPeriodicTask(
        celery.PeriodicTask
    ):
        run_every = settings.YAGA_APNS_FEEDBACK_RUN_EVERY

        def run(self):
            apns_provider.feedback()


class CleanStorageTask(
    celery.Task
):
    def run(self, key):
        full_path = key

        path = key.replace(settings.MEDIA_LOCATION, '')

        path = path.strip('/')

        try:
            default_storage.delete(path)
            cloudfront_storage.delete(full_path)
        except Exception as e:
            logger.error(e)
            raise self.retry(exc=e)


class UploadProcessTask(
    celery.Task
):
    def run(self, key):
        if post_attachment_re.match(key):
            PostAttachmentProcessTask().delay(key)
        else:
            CleanStorageTask().delay(key)


class PostAttachmentProcessTask(
    celery.Task
):
    def run(self, key):
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

            try:
                is_valid_attachment = post.is_valid_attachment()
            except Exception as e:
                logger.exception(e)
                raise self.retry(exc=e)

            if is_valid_attachment:
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
    def run(self, pk):
        post = Post.objects.filter(
            pk=pk
        ).first()

        if post:
            try:
                transcoded = post.transcode()
            except Exception as e:
                logger.exception(e)
                raise self.retry(exc=e)

            if transcoded:
                post.mark_ready(
                    attachment_preview=post.attachment_preview
                )
            else:
                logger.error('Transcoding failed {file_obj}'.format(
                    file_obj=post.attachment.name
                ))
                raise self.retry()


class NotificationTask(
    celery.Task
):
    def run(self, instance, **kwargs):
        NotificationInstances._instances[instance].notify(**kwargs)


class APNSPushTask(
    celery.Task
):
    def run(self, receivers, **kwargs):
        if receivers:
            try:
                apns_provider.push(receivers, **kwargs)
            except Exception as e:
                logger.exception(e)
                raise self.retry(exc=e)


from .notifications import NotificationInstances  # noqa # isort:skip
