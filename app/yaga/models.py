from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import base64
import hashlib
import hmac
import json
import logging
import os

import magic
from django.db import connection, models, transaction
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import SimpleLazyObject
from django.utils.translation import ugettext_lazy as _
from djorm_pgarray.fields import TextArrayField
from model_utils import FieldTracker

from app.managers import AtomicManager
from app.model_fields import PhoneNumberField, UUIDField

from .choices import StateChoice, VendorChoice
from .conf import settings

# from .tasks import CleanStorageTask

logger = logging.getLogger(__name__)

_provider = None


def get_lazy_provider():
    def _get_lazy_provider():
        global _provider

        if _provider is None:
            from .providers import code_provider

            _provider = code_provider

        return _provider

    return SimpleLazyObject(_get_lazy_provider)


def code_expire_at():
    return timezone.now() + settings.YAGA_SMS_EXPIRATION


def post_upload_to(instance, filename=None, prefix=None):
    return os.path.join(
        prefix,
        str(instance.group.pk),
        str(instance.pk)
    )


def post_attachment_upload_to(instance, filename=None):
    return post_upload_to(
        instance,
        filename=filename,
        prefix=settings.YAGA_ATTACHMENT_PREFIX
    )


def post_attachment_upload_to_trash(instance, filename=None):
    return post_upload_to(
        instance,
        filename=filename,
        prefix='trash'
    )

post_attachment_preview_upload_to = post_attachment_upload_to_trash  # backward


@python_2_unicode_compatible
class Code(
    models.Model
):
    provider = get_lazy_provider()

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
        return str(self.request_id)


@python_2_unicode_compatible
class Member(
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
        return self.user.phone.as_e164


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

    tracker = FieldTracker()

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')
        permissions = (
            ('view_group', 'Can view Group'),
        )

    def member_count(self):
        return self.member_set.count()
    member_count.short_description = _('Members Count')

    def post_count(self):
        return self.post_set.count()
    post_count.short_description = _('Posts Count')

    def mark_updated(self):
        self.save(update_fields=['updated_at'])

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

    name_x = models.PositiveSmallIntegerField(
        verbose_name=_('Name X'),
        blank=True,
        null=True
    )

    name_y = models.PositiveSmallIntegerField(
        verbose_name=_('Name Y'),
        blank=True,
        null=True
    )

    font = models.PositiveSmallIntegerField(
        verbose_name=_('Font'),
        blank=True,
        null=True
    )

    rotation = models.PositiveSmallIntegerField(
        verbose_name=_('Rotation'),
        blank=True,
        null=True
    )

    scale = models.PositiveSmallIntegerField(
        verbose_name=_('Scale'),
        blank=True,
        null=True
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('User')
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

    tracker = FieldTracker()

    objects = models.Manager()
    atomic_objects = AtomicManager()

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        permissions = (
            ('view_post', 'Can view Post'),
        )
        unique_together = (
            ('checksum', 'group'),
        )

    @property
    def ready(self):
        return self.state == self.state_choices.READY

    @ready.setter
    def ready_setter(self, value):
        if value:
            self.state = self.state_choices.READY
        else:
            raise NotImplementedError

    @property
    def deleted(self):
        return self.state == self.state_choices.DELETED

    @deleted.setter
    def deleted_setter(self, value):
        if value:
            self.state = self.state_choices.DELETED
        else:
            raise NotImplementedError

    @property
    def atomic(self):
        try:
            post = Post.atomic_objects.get(
                pk=self.pk
            )
            return post
        except Post.DoesNotExist:
            return False

    def atomic_delete(self):
        with transaction.atomic():
            post = self.atomic

            if post:
                post.delete()

    def mark_uploaded(self):
        with transaction.atomic():
            post = self.atomic

            if post:
                post.path = self.path

                post.checksum = self.checksum

                if post.deleted:
                    post.ready = True

                    post.clean_storage()

                    return

                if not post.ready:
                    post.ready = True

                    post.push()

                    post.save()
                else:
                    post.clean_storage()

    def mark_deleted(self, save=True):
        with transaction.atomic():
            post = self.atomic

            if post:
                post.clean_storage(save=False)

                if not self.deleted:
                    self.deleted = True

                if save:
                    self.save()

    def clean_storage(self, save=True):
        self.checksum = None

        if self.attachment:
            # path = self.attachment.name

            self.attachment = None

            def delete_attachment():
                # CleanStorageTask().delay(path)
                pass

            connection.on_commit(delete_attachment)

        if save:
            self.save()

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

    def is_valid_attachment(self):
        if not self.attachment:
            return False

        for chunk in self.attachment.chunks():
            header = chunk
            break

        mime = self.get_mime(header)

        if mime != settings.YAGA_AWS_UPLOAD_MIME:
            logger.error('{file_name} unexpected mime {mime}'.format(
                file_name=self.attachment.name,
                mime=mime
            ))

            return False

        if (
            self.attachment.size
            >
            settings.YAGA_AWS_UPLOAD_MAX_LENGTH
        ):
            logger.error('{file_name} exceeded capacity'.format(
                file_name=self.attachment.name
            ))

            return False

        if self.attachmentj.size == 0:
            logger.error('{file_name} size is 0'.format(
                file_name=self.attachment.name
            ))

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

    def save(self, *args, **kwargs):
        if self.checksum == '':
            self.checksum = None

        if self.pk:
            if not kwargs.get('update_fields'):
                changes = list(self.tracker.changed().keys())

                changes = list(filter(
                    lambda change: (
                        self.tracker.previous(change)
                        !=
                        getattr(self, change)
                    ),
                    changes
                ))

                kwargs['update_fields'] = changes

            if 'updated_at' not in kwargs['update_fields']:
                kwargs['update_fields'] = list(kwargs['update_fields'])
                kwargs['update_fields'].append('updated_at')

        return super(Post, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.clean_storage(save=False)
        return super(Post, self).delete(*args, **kwargs)

    def __str__(self):
        return str(self.pk)


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
        verbose_name=_('phone'),
        blank=True
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
