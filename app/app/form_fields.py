from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from phonenumber_field.formfields import \
    PhoneNumberField as BasePhoneNumberField


class PhoneNumberField(
    BasePhoneNumberField
):
    def to_python(self, value):
        if not value.startswith('+'):
            value = '+' + value

        return super(PhoneNumberField, self).to_python(value)
