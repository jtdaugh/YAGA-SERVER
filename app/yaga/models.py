from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import base64
import hashlib
import hmac
import json
import os

import magic
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from app.model_fields import PhoneNumberField, UUIDField
from app.utils import smart_text

from .conf import settings
from .providers import NexmoProvider


def code_expire_at():
    return timezone.now() + settings.YAGA_SMS_EXPIRATION


def post_upload_to(instance, filename=None):
    return os.path.join(
        'posts',
        str(instance.group.pk),
        str(instance.pk)
    )


@python_2_unicode_compatible
class Code(
    models.Model
):
    provider = NexmoProvider()

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
        db_index=True,
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
        return self.request_id


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
        verbose_name=_('User'),
        db_index=True
    )

    group = models.ForeignKey(
        'Group',
        verbose_name=_('Group'),
        db_index=True
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

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Member',
        verbose_name=_('Members'),
        db_index=True
    )

    created_at = models.DateTimeField(
        verbose_name=_('Created At'),
        auto_now_add=True
    )

    def members_count(self):
        return self.member_set.count()
    members_count.short_description = _('Members Count')

    def posts_count(self):
        return Post.objects.filter(
            group=self
        ).count()
    posts_count.short_description = _('Posts Count')

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')

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

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('User'),
        db_index=True
    )

    group = models.ForeignKey(
        Group,
        verbose_name=_('Group'),
        db_index=True
    )

    attachment = models.FileField(
        verbose_name=_('Attachment'),
        db_index=True,
        upload_to=post_upload_to,
        blank=True,
        null=True
    )

    checksum = models.CharField(
        verbose_name=_('Checksum'),
        max_length=255,
        db_index=True,
        blank=True,
        null=True
    )

    mime = models.CharField(
        verbose_name=_('Mime'),
        max_length=255,
        db_index=True,
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

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    # def get_checksum(self, chunks):
    #     md5 = hashlib.md5()

    #     for data in chunks:
    #         md5.update(data)

    #     return md5.hexdigest()

    def likes(self):
        return self.like_set.count()

    def get_mime(self, stream):
        return magic.from_buffer(stream, mime=True)

    def set_meta(self):
        stream = self.attachment.file.key.read(1024)

        self.mime = self.get_mime(stream)

        self.checksum = self.attachment.file.key.etag.strip('"')

    def is_valid(self):
        if not self.attachment:
            return False

        if self.mime != settings.YAGA_AWS_ALLOWED_MIME:
            return False

        if self.attachment.file.size > settings.YAGA_AWS_UPLOAD_MAX_LENGTH:
            return False

        if self.attachment.file.size == 0:
            return False

        return True

    def sign_s3(self):
        access_key = settings.AWS_ACCESS_KEY_ID
        secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        bucket = settings.AWS_STORAGE_BUCKET_NAME

        content_type = settings.YAGA_AWS_ALLOWED_MIME

        expires_in = timezone.now() + settings.YAGA_AWS_UPLOAD_EXPIRES

        expires = expires_in.strftime('%Y-%m-%dT%H:%M:%S.000Z')

        acl = 'public-read'

        key = os.path.join(
            settings.MEDIA_LOCATION,
            post_upload_to(self)
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
        verbose_name=_('User'),
        db_index=True
    )

    post = models.ForeignKey(
        Post,
        verbose_name=_('Post'),
        db_index=True
    )

    created_at = models.DateTimeField(
        verbose_name=_('Created At'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('Like')
        verbose_name_plural = _('Likes')
        unique_together = (
            ('user', 'post'),
        )

    def __str__(self):
        return smart_text(self.pk)


from . import dispatch  # noqa # isort:skip
