from __future__ import absolute_import, division, unicode_literals

import datetime

from django.utils.translation import ugettext_lazy as _
from rest_framework.serializers import (
    CharField, ValidationError, DateTimeField
)
from phonenumber_field.phonenumber import to_python


class PhoneField(
    CharField
):
    def to_internal_value(self, data):
        data = super(PhoneField, self).to_internal_value(data)

        if not data.startswith('+'):
            data = '+' + data

        phone_number = to_python(data)

        if phone_number and not phone_number.is_valid():
            raise ValidationError(_('Incorrect phone format.'))

        return phone_number.as_e164


class CodeField(
    CharField
):
    def to_internal_value(self, data):
        data = super(CodeField, self).to_internal_value(data)

        try:
            int(data)
        except:
            raise ValidationError(_('Incorrect code format.'))

        return data


class TimeStampField(
    DateTimeField
):
    def to_internal_value(self, data):
        try:
            data = datetime.datetime.fromtimestamp(float(data))
        except:
            raise ValidationError(_('Incorrect timestamp format.'))

        return data
