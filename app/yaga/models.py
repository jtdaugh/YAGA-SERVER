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

    def __str__(self):
        return self.request_id
