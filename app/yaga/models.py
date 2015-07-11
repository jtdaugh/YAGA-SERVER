from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)
from future.types.newstr import newstr

import base64
import hashlib
import hmac
import json
import logging
import os
import tempfile

import magic
from celery import states as celery_states
from django.core.files.base import File
from django.core.files.storage import default_storage
from django.db import connection, models, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from djorm_pgarray.fields import TextArrayField
from model_utils import FieldTracker

from app.managers import AtomicManager
from app.model_fields import PhoneNumberField, UUIDField
from app.utils import sh, u
from requestprovider import get_request

from .choices import StateChoice, StatusChoice, VendorChoice
from .conf import settings

logger = logging.getLogger(__name__)


def code_expire_at():
    return timezone.now() + settings.YAGA_SMS_EXPIRATION


def post_upload_to(instance, filename=None, prefix=None):
    path = str(os.path.join(
        prefix,
        str(instance.group.pk),
        str(instance.pk)
    ))

    if isinstance(path, newstr):
        path = path.__str__()

    return u(path)


def post_attachment_upload_to(instance, filename=None):
    return post_upload_to(
        instance,
        filename=filename,
        prefix=settings.YAGA_ATTACHMENT_PREFIX
    )


def post_attachment_preview_upload_to_trash(instance, filename=None):
    return post_upload_to(
        instance,
        filename=filename,
        prefix=settings.YAGA_ATTACHMENT_TRASH_PREFIX
    )


def post_attachment_preview_upload_to(instance, filename=None):
    return post_upload_to(
        instance,
        filename=filename,
        prefix=settings.YAGA_ATTACHMENT_PREVIEW_PREFIX
    )


def post_attachment_server_preview_upload_to(instance, filename=None):
    return post_upload_to(
        instance,
        filename=filename,
        prefix=settings.YAGA_ATTACHMENT_SERVER_PREVIEW_PREFIX
    )


@python_2_unicode_compatible
class Code(
    models.Model
):
    request_id = models.CharField(
        verbose_name=_('Request Id'),
        primary_key=True,
        max_length=255
    )

    phone = PhoneNumberField(
        verbose_name=_('Phone Number'),
        max_length=255,
        unique=True
    )

    expire_at = models.DateTimeField(
        verbose_name=_('Expire At'),
        default=code_expire_at,
        db_index=True
    )

    @property
    def provider(self):
        return code_provider

    def check_code(self, code):
        response = self.provider.check(self.request_id, code)

        return response

    def verify_phone(self):
        response = self.provider.verify(self.phone.as_e164)

        self.request_id = response.request_id

        return self.request_id

    class Meta:
        verbose_name = _('Code')
        verbose_name_plural = _('Codes')

    def __str__(self):
        return str(self.pk)


@python_2_unicode_compatible
class Member(
    models.Model
):
    status_choices = StatusChoice()

    id = UUIDField(
        auto=True,
        primary_key=True,
        version=4
    )

    status = models.PositiveSmallIntegerField(
        verbose_name=_('Status'),
        choices=status_choices,
        db_index=True,
        default=status_choices.MEMBER
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('User')
    )

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Creator'),
        related_name='member_creator'
    )

    group = models.ForeignKey(
        'Group',
        verbose_name=_('Group')
    )

    mute = models.BooleanField(
        verbose_name=_('Mute'),
        db_index=True,
        default=False
    )

    joined_at = models.DateTimeField(
        verbose_name=_('Joined At'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('Member')
        verbose_name_plural = _('Members')
        # auto_created = True
        unique_together = (
            ('user', 'group'),
        )

    def __str__(self):
        return str(self.pk)


@python_2_unicode_compatible
class Group(
    models.Model
):
    id = UUIDField(
        auto=True,
        primary_key=True,
        version=4
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
    )

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Creator'),
        related_name='group_creator'
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Member',
        through_fields=('group', 'user'),
        verbose_name=_('Members')
    )

    created_at = models.DateTimeField(
        verbose_name=_('Created At'),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name=_('Updated At'),
        auto_now=True,
        db_index=True
    )

    private = models.BooleanField(
        verbose_name=_('Private'),
        default=True,
        db_index=True
    )

    tracker = FieldTracker()

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')
        permissions = (
            ('view_group', 'Can view Group'),
        )

    def visible_post_count(self):
        return self.post_set.filter(
            state__in=[
                Post.state_choices.READY,
                Post.state_choices.DELETED
            ],
            approved=True
        ).count()

    def member_count(self):
        return self.member_set.count()
    member_count.short_description = _('Members Count')

    def post_count(self):
        return self.post_set.count()
    post_count.short_description = _('Posts Count')

    def last_foreign_post(self):
        request = get_request()

        last_post = self.post_set.filter(
            state=Post.state_choices.READY,
            approved=True,
        ).exclude(
            user=request.user
        ).order_by(
            '-ready_at'
        ).first()

        if last_post:
            last_post = last_post.pk

        return last_post

    def mark_updated(self):
        self.save(update_fields=['updated_at'])

    def active_member_set(self):
        return [
            member for member in self.member_set.all()
            if member.status == Member.status_choices.MEMBER
        ]

    def pending_member_set(self):
        return [
            member for member in self.member_set.all()
            if member.status == Member.status_choices.PENDING
        ]

    def __str__(self):
        return str(self.pk)


@python_2_unicode_compatible
class Post(
    models.Model
):
    id = UUIDField(
        auto=True,
        primary_key=True,
        version=1
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        blank=True,
        null=True
    )

    namer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Namer'),
        related_name='post_namer',
        null=True,
        blank=True
    )

    font = models.PositiveSmallIntegerField(
        verbose_name=_('Font'),
        blank=True,
        null=True
    )

    name_x = models.DecimalField(
        verbose_name=_('Name X'),
        max_digits=7, decimal_places=4,
        blank=True,
        null=True
    )

    name_y = models.DecimalField(
        verbose_name=_('Name Y'),
        max_digits=7, decimal_places=4,
        blank=True,
        null=True
    )

    rotation = models.DecimalField(
        verbose_name=_('Rotation'),
        max_digits=7, decimal_places=4,
        blank=True,
        null=True
    )

    scale = models.DecimalField(
        verbose_name=_('Scale'),
        max_digits=7, decimal_places=4,
        blank=True,
        null=True
    )

    miscellaneous = models.CharField(
        verbose_name=_('Miscellaneous'),
        max_length=255,
        blank=True,
        null=True
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('User'),
        related_name='post_user'
    )

    group = models.ForeignKey(
        Group,
        verbose_name=_('Group')
    )

    attachment = models.FileField(
        verbose_name=_('Attachment'),
        upload_to=post_attachment_upload_to,
        blank=True,
        null=False,
        default=''
    )

    attachment_preview = models.FileField(
        verbose_name=_('Attachment Preview'),
        upload_to=post_attachment_server_preview_upload_to,
        blank=True,
        null=False,
        default=''
    )

    checksum = models.CharField(
        verbose_name=_('Checksum'),
        max_length=255,
        blank=True,
        null=True
    )

    state_choices = StateChoice()

    state = models.PositiveSmallIntegerField(
        verbose_name=_('State'),
        choices=state_choices,
        db_index=True,
        default=state_choices.PENDING
    )

    created_at = models.DateTimeField(
        verbose_name=_('Created At'),
        auto_now_add=True
    )

    ready_at = models.DateTimeField(
        verbose_name=_('Ready At'),
        blank=True,
        null=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        verbose_name=_('Updated At'),
        auto_now=True,
        db_index=True
    )

    upload_version = models.PositiveIntegerField(
        verbose_name=_('Upload Client Version'),
        default=0
    )

    approved = models.BooleanField(
        verbose_name=('Approved'),
        default=True,
        db_index=True
    )

    tracker = FieldTracker()

    objects = models.Manager()
    atomic_objects = AtomicManager()

    def dummy_likes(self):
        return []

    def dummy_namer(self):
        return None

    def dummy_user(self):
        class DummyUser(
            object
        ):
            def __init__(self):
                self.id = self.pk = 'e341918e-fa98-44cd-b103-bebe468cdd69'
                self.phone = '+380632237710'
                self.name = 'hellysmile'

        return DummyUser()

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        permissions = (
            ('view_post', 'Can view Post'),
            ('approve_post', 'Can approve Post')
        )
        unique_together = (
            ('checksum', 'group'),
        )

    def save(self, *args, **kwargs):
        kwargs.setdefault('force', False)

        force = kwargs.pop('force')

        if self.checksum == '':
            self.checksum = None

        if self.pk and not force:
            update_fields = list(kwargs.get('update_fields', []))

            if update_fields == ['updated_at']:
                super(Post, self).save(*args, **kwargs)
            else:
                changes = list(self.tracker.changed().keys())

                changes = list(filter(
                    lambda change: (
                        self.tracker.previous(change)
                        !=
                        getattr(self, change)
                    ),
                    changes
                ))

                updates = set(changes) | set(update_fields)

                if updates:
                    updates.add('updated_at')

                    kwargs['update_fields'] = list(updates)

                    super(Post, self).save(*args, **kwargs)
        else:
            super(Post, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.clean_storage()
        self.purge_copies()
        super(Post, self).delete(*args, **kwargs)

    def __str__(self):
        return str(self.pk)

    def purge_copies(self):
        for copy in PostCopy.objects.filter(
            Q(post=self)
            |
            Q(parent=self)
        ):
            copy.delete()

    @property
    def ready(self):
        return self.state in [
            Post.state_choices.DELETED,
            Post.state_choices.READY
        ]

    @property
    def deleted(self):
        return self.state == Post.state_choices.DELETED

    class TmpAttachment(object):
        def __init__(self, instance):
            self.instance = instance

        def __enter__(self):
            self.f = tempfile.NamedTemporaryFile(delete=False)

            for chunk in self.instance.attachment.chunks():
                self.f.write(chunk)

            self.f.flush()
            self.f.close()

            return self.f

        def __exit__(self, type, value, traceback):
            try:
                os.unlink(self.f.name)
            except IOError:
                pass

    def notify(self):
        if self.group.private:
            PostGroupNotification.schedule(
                post=self.pk
            )

    def mark_approved(self):
        with transaction.atomic():
            post = self.atomic

            if post:
                if not post.approved:
                    post.approved = True

                    if post.state == Post.state_choices.READY:
                        post.group.mark_updated()

                        ApprovedDirectNotification.schedule(
                            post=post.pk
                        )

                    post.save()

                return post

    def download_cache_boost(self):
        for url in [
            self.attachment_preview.url,
            self.attachment.url
        ]:
            def schedule_download_cache_boost():
                CoudfrontCacheBoostTask().delay(
                    [url]
                )

            connection.on_commit(schedule_download_cache_boost)

    def is_transcoded(self):
        if self.transcoding_result.state == celery_states.SUCCESS:
            return True

        return default_storage.exists(
            post_attachment_server_preview_upload_to(self)
        )

    @property
    def transcoding_task_id(self):
        return '{pk}_transcoding'.format(
            pk=str(self.pk)
        )

    @property
    def transcoding_result(self):
        result = TranscodingTask().AsyncResult(
            self.transcoding_task_id
        )
        return result

    def schedule_transcoding(self):
        TranscodingTask().apply_async(
            (self.pk,), task_id=self.transcoding_task_id
        )

    def get_transpose(self):
        if self.upload_version < settings.YAGA_CLIENT_VERSION_NO_TRANSPOSE:
            return 'transpose=1,'
        else:
            return ''

    def transcode(self):
        if self.is_transcoded():
            return True

        if not self.attachment:
            return False

        try:
            self.attachment.file
        except IOError:
            return False

        with self.TmpAttachment(self) as attachment:
            try:
                output = tempfile.NamedTemporaryFile(delete=False)
                output.flush()
                output.close()

                process = sh(
                    settings.YAGA_ATTACHMENT_TRANSCODE_CMD.format(
                        transpose=self.get_transpose(),
                        input=attachment.name,
                        output=output.name
                    )
                )

                if process:
                    if self.is_transcoded():
                        return True

                    with open(output.name, 'rb') as stream:
                        fd = File(stream)

                        self.attachment_preview.save(
                            post_attachment_server_preview_upload_to(self),
                            fd,
                            save=False
                        )

                        fd.close()

                        try:
                            self.attachment_preview.file.key.set_remote_metadata(  # noqa
                                {
                                    'Content-Type':
                                    'image/gif'
                                },
                                {},
                                True
                            )
                        except Exception:
                            pass

                        return True
                else:
                    logger.error(
                        '{file_name} transcoding process failed '
                        '\n stdout->{stdout} \n stderr->{stderr}'.format(
                            file_name=self.attachment.name,
                            stdout=process.stdout,
                            stderr=process.stderr
                        )
                    )
            finally:
                try:
                    os.unlink(output.name)
                except Exception:
                    pass

        return False

    @property
    def atomic(self):
        try:
            post = Post.atomic_objects.get(
                pk=self.pk
            )
            return post
        except Post.DoesNotExist:
            return False

    def update(self, **kwargs):
        for key, value in list(kwargs.items()):
            setattr(self, key, value)

    def mark_uploaded(self, transcode=True, **kwargs):
        with transaction.atomic():
            post = self.atomic

            if post:
                post.update(**kwargs)

                if post.state in [
                    Post.state_choices.UPLOADED,
                    Post.state_choices.READY
                ]:
                    post.mark_deleted()

                    logger.error(
                        'Attempt to override {group_id}/{post_id}'.format(
                            group_id=post.group.pk,
                            post_id=post.pk
                        )
                    )
                elif post.state == Post.state_choices.DELETED:
                    post.mark_deleted()

                    logger.error(
                        'Deleted due state {group_id}/{post_id}'.format(
                            group_id=post.group.pk,
                            post_id=post.pk
                        )
                    )
                elif post.is_duplicate():
                    post.mark_deleted()

                    logger.error(
                        'Dropped duplicate {group_id}/{post_id}'.format(
                            group_id=post.group.pk,
                            post_id=post.pk
                        )
                    )
                else:
                    post.state = Post.state_choices.UPLOADED

                    if transcode:
                        connection.on_commit(self.schedule_transcoding)

                    post.save()

                    return post

    def mark_ready(self, **kwargs):
        with transaction.atomic():
            post = self.atomic

            if post:
                post.update(**kwargs)

                if post.state == Post.state_choices.DELETED:
                    post.mark_deleted()
                elif post.state == Post.state_choices.READY:
                    post.save()

                    return True
                elif post.state == Post.state_choices.UPLOADED:
                    post.state = Post.state_choices.READY
                    post.ready_at = timezone.now()

                    post.download_cache_boost()

                    post.notify()

                    post.save()

                    post.group.mark_updated()

                    for copy in PostCopy.objects.filter(
                        parent=post
                    ):
                        copy.schedule()

                    return post

    # def mark_canceled(self):
    #     with transaction.atomic():
    #         post = self.atomic

    #         if post:
    #             if post.state not in (
    #                 Post.state_choices.DELETED,
    #                 Post.state_choices.READY
    #             ):
    #                 post.state = Post.state_choices.CANCELED
    #                 post.ready_at = timezone.now()
    #                 post.clean_storage()
    #                 self.clean_storage()
    #                 post.save()

    def mark_deleted(self):
        with transaction.atomic():
            post = self.atomic

            if post:
                post.state = Post.state_choices.DELETED
                post.ready_at = timezone.now()
                post.clean_storage()
                post.save()

                post.purge_copies()

    def clean_storage(self, path=None):
        if path is not None:
            if isinstance(path, (list, tuple)):
                for item in path:
                    def delete_item():
                        CleanStorageTask().delay(item)

                    connection.on_commit(delete_item)
            else:
                def delete_path():
                    CleanStorageTask().delay(path)

                connection.on_commit(delete_path)

        self.checksum = None

        self.attachment = ''

        attachment_path = post_attachment_upload_to(
            self
        )

        def delete_attachment():
            CleanStorageTask().delay(attachment_path)

        connection.on_commit(delete_attachment)

        attachment_preview_path = post_attachment_server_preview_upload_to(
            self
        )

        def delete_attachment_preview():
            CleanStorageTask().delay(attachment_preview_path)

        connection.on_commit(delete_attachment_preview)

        old_attachment_preview_path = post_attachment_preview_upload_to(
            self
        )

        def delete_old_attachment_preview():
            CleanStorageTask().delay(old_attachment_preview_path)

        connection.on_commit(delete_old_attachment_preview)

    def mark_updated(self):
        self.save(update_fields=['updated_at'])

    def like_count(self):
        return self.like_set.count()
    like_count.short_description = _('Like Count')

    def get_mime(self, stream):
        return magic.from_buffer(stream, mime=True)

    def get_checksum(self):
        try:
            return self.attachment.file.key.etag.strip('"')
        except Exception:
            md5 = hashlib.md5()

            for chunk in self.attachment.chunks():
                md5.update(chunk)

            return md5.hexdigest()

    def is_duplicate(self):
        return Post.objects.filter(
            group=self.group,
            checksum=self.checksum
        ).exists()

    def is_valid_attachment(self):
        if not self.attachment:
            return False

        try:
            self.attachment.file
        except IOError:
            return False

        for chunk in self.attachment.chunks():
            header = chunk
            break

        mime = self.get_mime(header)

        if mime != settings.YAGA_AWS_UPLOAD_MIME:
            logger.error('{group_id}/{post_id} unexpected mime {mime}'.format(
                group_id=self.group.pk,
                post_id=self.pk,
                mime=mime
            ))

            return False

        if (
            self.attachment.size
            >
            settings.YAGA_AWS_UPLOAD_MAX_LENGTH
        ):
            logger.error('{group_id}/{post_id} size is {size}'.format(
                group_id=self.group.pk,
                post_id=self.pk,
                size=self.attachment.size
            ))

            return False

        if self.attachment.size == 0:
            logger.error('{group_id}/{post_id} size is 0'.format(
                group_id=self.group.pk,
                post_id=self.pk
            ))

            return False

        with self.TmpAttachment(self) as attachment:
            process = sh(
                settings.YAGA_ATTACHMENT_VALIDATE_CMD.format(
                    path=attachment.name
                )
            )

            if process:
                for key, value in settings.YAGA_ATTACHMENT_VALIDATE_RULES:
                    for line in process.stderr.splitlines():
                        if key in line:
                            if value not in line:
                                logger.error(
                                    '{group_id}/{post_id} validation '
                                    'key "{key}" with "{value}" '
                                    'not in "{line}"'.format(
                                        group_id=self.group.pk,
                                        post_id=self.pk,
                                        key=key,
                                        value=value,
                                        line=line
                                    )
                                )

                                return False
            else:
                logger.error(
                    '{group_id}/{post_id} validation process failed\n'
                    'stdout->{stdout}\nstderr->{stderr}'.format(
                        group_id=self.group.pk,
                        post_id=self.pk,
                        stdout=process.stdout,
                        stderr=process.stderr
                    )
                )

                return False

        return True

    def sign_s3(self, mime, path_fn):
        access_key = settings.AWS_ACCESS_KEY_ID
        secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        bucket = settings.AWS_STORAGE_BUCKET_NAME

        content_type = mime

        expires_in = timezone.now() + settings.YAGA_AWS_UPLOAD_EXPIRES

        expires = expires_in.strftime('%Y-%m-%dT%H:%M:%S.000Z')

        acl = 'public-read'

        key = os.path.join(
            settings.MEDIA_LOCATION,
            path_fn(self)
        )

        policy_object = json.dumps({
            'expiration': expires,
            'conditions': [
                {
                    'bucket': bucket
                },
                {
                    'acl': acl
                },
                {
                    'Content-Type': content_type
                },
                {
                    'key': key
                },
                [
                    'content-length-range',
                    1,
                    settings.YAGA_AWS_UPLOAD_MAX_LENGTH
                ],
            ]
        })

        policy = base64.b64encode(
            policy_object.replace('\n', '').replace('\r', '').encode()
        )

        signature = hmac.new(
            secret_access_key.encode(),
            policy,
            hashlib.sha1
        ).digest()

        signature = base64.b64encode(signature)

        bucket_url = settings.S3_HOST

        return {
            'endpoint': bucket_url,
            'fields': {
                'key': key,
                'acl': acl,
                'policy': policy.decode(),
                'signature': signature.decode(),
                'AWSAccessKeyId': access_key,
                'Content-Type': content_type
            }
        }


@python_2_unicode_compatible
class Like(
    models.Model
):
    id = UUIDField(
        auto=True,
        primary_key=True,
        version=4
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('User')
    )

    post = models.ForeignKey(
        Post,
        verbose_name=_('Post')
    )

    created_at = models.DateTimeField(
        verbose_name=_('Created At'),
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = _('Like')
        verbose_name_plural = _('Likes')
        unique_together = (
            ('user', 'post'),
        )

    def __str__(self):
        return str(self.pk)


@python_2_unicode_compatible
class Device(
    models.Model
):
    id = UUIDField(
        auto=True,
        primary_key=True,
        version=4
    )

    vendor_choices = VendorChoice()

    vendor = models.PositiveSmallIntegerField(
        verbose_name=_('Vendor'),
        choices=vendor_choices,
        db_index=True
    )

    locale = models.CharField(
        verbose_name=_('Locale'),
        max_length=2
    )

    token = models.CharField(
        verbose_name=_('Token'),
        max_length=255,
        db_index=True
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('User')
    )

    created_at = models.DateTimeField(
        verbose_name=_('Created At'),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name=_('Updated At'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Device')
        verbose_name_plural = _('Devices')
        unique_together = (
            ('vendor', 'token'),
        )

    def __str__(self):
        return str(self.pk)


@python_2_unicode_compatible
class Contact(
    models.Model
):
    id = UUIDField(
        auto=True,
        primary_key=True,
        version=4
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('User')
    )

    phones = TextArrayField(
        verbose_name=_('Phones'),
        # dbtype='character varying(255)',
        blank=False
    )
    # here is GIN index at migration

    created_at = models.DateTimeField(
        verbose_name=_('Created At'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')

    def __str__(self):
        return str(self.pk)


@python_2_unicode_compatible
class PostCopy(
    models.Model
):
    id = UUIDField(
        auto=True,
        primary_key=True,
        version=4
    )

    group = models.ForeignKey(
        'Group',
        verbose_name=_('Group')
    )

    parent = models.ForeignKey(
        Post,
        verbose_name=_('parent'),
        related_name='post_parent'
    )

    post = models.ForeignKey(
        Post,
        verbose_name=_('Post'),
        related_name='post_post'
    )

    created_at = models.DateTimeField(
        verbose_name=_('Created At'),
        auto_now_add=True
    )

    copy_attrs = (
        'name', 'namer',
        'font', 'name_x', 'name_y', 'rotation', 'scale', 'miscellaneous'
    )

    def schedule(self):
        def copy():
            PostCopyTask().delay(self.pk)

        connection.on_commit(copy)

    def cancel(self, *instances):
        self.post.delete()
        self.delete()

    def copy_attachment(self):
        path = self.copy(
            self.parent.attachment,
            post_attachment_upload_to
        )

        if path:
            try:
                self.post.attachment = path
                self.post.checksum = self.post.get_checksum()

                return self.post
            except Exception as e:
                logging.exception(e)

    def copy_attachment_preview(self):
        path = self.copy(
            self.parent.attachment_preview,
            post_attachment_server_preview_upload_to
        )

        if path:
            self.post.attachment_preview = path

            return self.post

    def copy(self, obj, path_fn):
        try:
            obj.file
        except IOError:
            return False

        try:
            path = path_fn(self.post)

            obj.file.key.copy(
                settings.AWS_STORAGE_BUCKET_NAME,
                default_storage._normalize_name(path),
                preserve_acl=True
            )

            return path
        except Exception as e:
            logger.exception(e)

            return False

    class Meta:
        verbose_name = _('Post Copy')
        verbose_name_plural = _('Post Copies')
        unique_together = (
            ('parent', 'group'),
        )

    def __str__(self):
        return str(self.pk)


@python_2_unicode_compatible
class MonkeyUser(
    models.Model
):
    id = UUIDField(
        auto=True,
        primary_key=True,
        version=4
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('User')
    )

    class Meta:
        verbose_name = _('Monkey User')
        verbose_name_plural = _('Monkey Users')

    def __str__(self):
        return str(self.pk)


from .notifications import ApprovedDirectNotification, PostGroupNotification  # noqa # isort:skip
from .providers import code_provider  # noqa # isort:skip
from .tasks import (  # noqa # isort:skip
    CleanStorageTask, CoudfrontCacheBoostTask, PostCopyTask, TranscodingTask
)
