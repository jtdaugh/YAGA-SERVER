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
from cStringIO import StringIO

import magic
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import SimpleLazyObject
from django.utils.translation import ugettext_lazy as _
from djorm_pgarray.fields import TextArrayField
from model_utils import FieldTracker
from PIL import Image

from app.model_fields import PhoneNumberField, UUIDField
from app.utils import Choice, smart_text

from .conf import settings

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
        instance, filename=filename,
        prefix=settings.YAGA_ATTACHMENT_PREFIX
    )


def post_attachment_preview_upload_to(instance, filename=None):
    return post_upload_to(
        instance, filename=filename,
        prefix=settings.YAGA_ATTACHMENT_PREVIEW_PREFIX
    )


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
        return smart_text(self.request_id)


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
        return smart_text(self.user.phone.as_e164)


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

    def members_count(self):
        return self.member_set.count()
    members_count.short_description = _('Members Count')

    def posts_count(self):
        return Post.objects.filter(
            group=self
        ).count()
    posts_count.short_description = _('Posts Count')

    def mark_updated(self):
        self.save(update_fields=['updated_at'])

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')
        permissions = (
            ('view_group', 'Can view Group'),
        )

    def __str__(self):
        return smart_text(self.pk)


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

    attachment_preview = models.FileField(
        verbose_name=_('Attachment Preview'),
        upload_to=post_attachment_preview_upload_to,
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

    ready = models.BooleanField(
        verbose_name=_('Ready'),
        db_index=True,
        default=False
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

    deleted = models.BooleanField(
        verbose_name=_('Deleted'),
        default=False,
        db_index=True
    )

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        permissions = (
            ('view_post', 'Can view Post'),
        )
        unique_together = (
            ('checksum', 'group'),
        )

    tracker = FieldTracker()

    # def get_checksum(self, chunks):
    #     md5 = hashlib.md5()

    #     for data in chunks:
    #         md5.update(data)

    #     return md5.hexdigest()

    def mark_deleted(self):
        self.checksum = None
        self.deleted = True
        self.save()

    def mark_updated(self):
        self.save(update_fields=['updated_at'])

    def likes(self):
        return self.like_set.all().count()

    def get_mime(self, stream):
        return magic.from_buffer(stream, mime=True)

    def is_valid_file_obj(self, field):
        file_obj = getattr(self, field)

        if not file_obj:
            return False

        file_obj.file.seek(0)
        stream = file_obj.file.read()

        mime = self.get_mime(stream)

        if mime != settings.YAGA_AWS_ALLOWED_MIME[field]:
            logger.error('{file_name} unexpected mime {mime}'.format(
                file_name=file_obj.name,
                mime=mime
            ))

            return False

        if (
            file_obj.file.size
            >
            settings.YAGA_AWS_UPLOAD_MAX_LENGTH
        ):
            logger.error('{file_name} exceeded capacity'.format(
                file_name=file_obj.name
            ))

            return False

        if file_obj.file.size == 0:
            logger.error('{file_name} size is 0'.format(
                file_name=file_obj.name
            ))

            return False

        return True

    def is_valid_attachment(self):
        return self.is_valid_file_obj('attachment')

    def is_valid_attachment_preview(self):
        if self.is_valid_file_obj('attachment_preview'):
            try:
                self.attachment_preview.file.seek(0)
                stream = self.attachment_preview.file.read()

                image = Image.open(StringIO(stream))

                image_size = image.size

                image_size = {
                    'x': image_size[0],
                    'y': image_size[1]
                }
            except Exception as e:
                logger.exception(e)

                return False

            if image_size not in settings.YAGA_ATTACHMENT_PREVIEW_SIZE:
                logger.error('{file_name} GIF is {x}*{y}'.format(
                    file_name=self.attachment_preview.name,
                    x=image_size['x'],
                    y=image_size['y']
                ))

                return False

            return True
        else:
            return False

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
            secret_access_key.encode(), policy, hashlib.sha1
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
            if kwargs.get('update_fields'):
                if 'updated_at' not in kwargs['update_fields']:
                    kwargs['update_fields'] = list(kwargs['update_fields'])
                    kwargs['update_fields'].append('updated_at')

            return super(Post, self).save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     if kwargs.get('update_fields', None) is None:
    #         if self.pk:
    #             is_dirty = list(self.tracker.changed().keys())

    #             if is_dirty:
    #                 kwargs['update_fields'] = is_dirty

    #     return super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return smart_text(self.pk)


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
        return smart_text(self.pk)


@python_2_unicode_compatible
class Device(
    models.Model
):
    id = UUIDField(
        auto=True,
        primary_key=True,
        version=4
    )

    class Vendor(
        Choice
    ):
        IOS = 0
        IOS_VALUE = 'IOS'
        ANDROID = 1
        ANDROID_VALUE = 'ANDROID'
    VENDOR_CHOICES = (
        (Vendor.IOS, Vendor.IOS_VALUE),
        (Vendor.ANDROID, Vendor.ANDROID_VALUE)
    )
    vendor = models.PositiveSmallIntegerField(
        verbose_name=_('Vendor'),
        choices=VENDOR_CHOICES,
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
        return smart_text(self.pk)


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
        return smart_text(self.pk)


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
        return smart_text(self.pk)
