from __future__ import absolute_import, division, unicode_literals

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from .providers import NexmoProvider


def expire_at():
    return timezone.now() + settings.CONSTANTS.SMS_EXPIRATION


class Code(
    models.Model
):
    provider = NexmoProvider()

    request_id = models.CharField(
        verbose_name=_('Request Id'),
        max_length=255,
        unique=True,
        db_index=True
    )

    phone = PhoneNumberField(
        verbose_name=_('Phone Number'),
        max_length=255,
        unique=True,
        db_index=True
    )

    expire_at = models.DateTimeField(
        verbose_name=_('Expire At'),
        default=expire_at,
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

    def __unicode__(self):
        return self.request_id


class Member(
    models.Model
):
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

    def __unicode__(self):
        return '%s | %s' % (self.user, self.group)


class Group(
    models.Model
):
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
        return self.members.count()
    members_count.short_description = _('Members Count')

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')

    def __unicode__(self):
        return self.name


class Post(
    models.Model
):
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
        upload_to='posts',
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
    )

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def __unicode__(self):
        if self.attachment:
            return self.attachment.name

        return str(self.created_at)


from . import dispatch  # noqa
