from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import logging

from celery import states as celery_states
from celery.exceptions import SoftTimeLimitExceeded
from django.core.files.storage import default_storage
from django.utils import timezone
from requests.exceptions import HTTPError

from app import celery
from app.utils import get_requests_session

from .conf import settings
from .models import Code, Group, Post, PostCopy
from .providers import apns_provider
from .storage import cloudfront_storage
from .utils import post_attachment_re

logger = logging.getLogger(__name__)


if cloudfront_storage.enabled:
    class CloudfrontCleanStoragePeriodicTask(
        celery.PeriodicTask
    ):
        run_every = settings.YAGA_CLOUDFRONT_CLEAN_RUN_EVERY

        def run(self):
            try:
                cloudfront_storage.clean()
            except Exception as e:
                logger.exception(e)
                raise self.retry(exc=e)


if settings.YAGA_PERIODIC_CLEANUP:
    class CodeCleanupAtomicPeriodicTask(
        celery.AtomicPeriodicTask
    ):
        run_every = settings.YAGA_CODE_CLEANUP_RUN_EVERY

        def run(self):
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
                post.mark_deleted()

    class PostTranscodePeriodicTask(
        celery.PeriodicTask
    ):
        run_every = settings.YAGA_ATTACHMENT_TRANSCODE_RUN_EVERY

        def run(self):
            expired = (
                timezone.now() - settings.YAGA_ATTACHMENT_TRANSCODE_EXPIRES
            )

            deadline = (
                timezone.now() - settings.YAGA_ATTACHMENT_TRANSCODE_DEADLINE
            )

            for post in Post.objects.filter(
                created_at__lte=expired,
                state=Post.state_choices.UPLOADED
            ):
                if post.created_at < deadline:
                    post.mark_deleted()
                else:
                    result = post.transcoding_result

                    if result.state in (
                        celery_states.FAILURE,
                        celery_states.PENDING
                    ):
                        post.schedule_transcoding()

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

        path = key.replace(settings.MEDIA_LOCATION, '', 1)

        path = path.strip('/')

        try:
            default_storage.delete(path)
        except Exception as e:
            logger.exception(e)
            raise self.retry(exc=e)

        cloudfront_storage.schedule(full_path)


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
    soft_time_limit = settings.YAGA_ATTACHMENT_VALIDATE_TIMEOUT

    def run(self, key):
        path = key.replace(settings.MEDIA_LOCATION, '', 1)

        path = path.strip('/')

        prefix, group_pk, post_pk = path.split('/')

        try:
            post = Post.objects.get(
                group__pk=group_pk,
                pk=post_pk
            )
        except Post.DoesNotExist:
            CleanStorageTask().delay(path)

            logger.error('No model found {group_id}/{post_id}'.format(
                group_id=group_pk,
                post_id=post_pk
            ))
        else:
            post.attachment = path

            try:
                is_valid_attachment = post.is_valid_attachment()
            except SoftTimeLimitExceeded:
                raise self.retry()
            except Exception as e:
                logger.exception(e)
                raise self.retry(exc=e)

            if is_valid_attachment:
                try:
                    post.checksum = post.get_checksum()
                except Exception as e:
                    logger.exception(e)
                    post.mark_deleted()
                else:
                    post.mark_uploaded(
                        attachment=post.attachment.name,
                        checksum=post.checksum
                    )
            else:
                post.mark_deleted()


class TranscodingTask(
    celery.Task
):
    soft_time_limit = settings.YAGA_ATTACHMENT_TRANSCODE_TIMEOUT

    def run(self, pk):
        post = Post.objects.filter(
            pk=pk
        ).first()

        if post and post.state == Post.state_choices.UPLOADED:
            try:
                transcoded = post.transcode()
            except SoftTimeLimitExceeded:
                raise self.retry()
            except Exception as e:
                logger.exception(e)
                raise self.retry(exc=e)

            if transcoded:
                post.mark_ready(
                    attachment_preview=post.attachment_preview
                )
            else:
                logger.error('Transcoding failed {group}/{post}'.format(
                    group=post.group.pk,
                    post=post.pk
                ))
                raise self.retry()


class CoudfrontCacheBoostTask(
    celery.Task
):
    def run(self, urls):
        session = get_requests_session()

        for url in urls:
            try:
                session.get(url)
            except HTTPError:
                pass


class PostCopyTask(
    celery.Task
):
    def run(self, copy_pk):
        copy = PostCopy.objects.select_related(
            'post',
            'parent'
        ).filter(
            pk=copy_pk
        ).first()

        if copy:
            try:
                success = False

                if copy.parent.state == Post.state_choices.READY:
                    attachment, checksum = copy.copy_attachment()

                    if attachment and checksum:
                        copied = copy.post.mark_uploaded(
                            transcode=False,
                            attachment=attachment,
                            checksum=checksum
                        )

                        if copied:
                            copy.post = copied

                        if copy.post.state == Post.state_choices.UPLOADED:
                            attachment_preview = copy.copy_attachment_preview()

                            if attachment_preview:
                                copy.post = copy.post.mark_ready(
                                    attachment_preview=attachment_preview
                                )

                                if (
                                    copy.post
                                    and
                                    copy.post.state == Post.state_choices.READY
                                ):
                                    success = True
            except SoftTimeLimitExceeded:
                pass

            if not success:
                copy.cancel()


class NotificationTask(
    celery.Task
):
    def run(self, instance, **kwargs):
        NotificationInstances.get_instance(instance)(
            **kwargs
        ).notify()


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
