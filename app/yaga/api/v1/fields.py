from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import datetime

from django.utils.translation import ugettext_lazy as _
from rest_framework.serializers import (
    CharField, DateTimeField, ValidationError, empty
)


class CodeField(
    CharField
):
    def to_internal_value(self, data):
        data = super(CodeField, self).to_internal_value(data)

        try:
            int(data)
        except Exception:
            raise ValidationError(_('Incorrect code format.'))

        return data


class TimeStampField(
    DateTimeField
):
    def to_internal_value(self, data):
        try:
            data = datetime.datetime.fromtimestamp(float(data))
        except Exception:
            raise ValidationError(_('Incorrect timestamp format.'))

        return data

# cache char list
allowed_chr = list(set(list(map(
    chr,
    [0x0023] +
    list(range(0x0030, 0x0039 + 1)) +
    list(range(0x0041, 0x005A + 1)) +
    list(range(0x0061, 0x007A + 1)) +
    list(range(0x00C0, 0x00D6 + 1)) +
    list(range(0x00D8, 0x00F6 + 1)) +
    list(range(0x00F8, 0x00FF + 1)) +
    list(range(0x0100, 0x017E + 1)) +
    list(range(0x0374, 0x0378 + 1)) +
    list(range(0x037b, 0x037e + 1)) +
    list(range(0x0386, 0x038a + 1)) +
    list(range(0x038e, 0x03a1 + 1)) +
    list(range(0x03a3, 0x03FC + 1)) +
    list(range(0x0400, 0x0481 + 1)) +
    list(range(0x048A, 0x04FF + 1)) +
    list(range(0x0531, 0x053B + 1)) +
    list(range(0x05F0, 0x05F2 + 1)) # +
    # list(range(0x1F300, 0x1F32C + 1)) +
    # list(range(0x1F330, 0x1F37D + 1)) +
    # list(range(0x1F380, 0x1F3CE + 1)) +
    # list(range(0x1F3D4, 0x1F3F7 + 1)) +
    # list(range(0x1F400, 0x1F4FE + 1)) +
    # list(range(0x1F500, 0x1F54A + 1)) +
    # list(range(0x1F550, 0x1F579 + 1)) +
    # list(range(0x1F57B, 0x1F5A3 + 1)) +
    # list(range(0x1F5A5, 0x1F5FF + 1))
))))

allowed_non_leading_chr = list(map(
    chr,
    [0x0021, 0x002A, 0x002B, 0x002D, 0x005F, 0x002E, 0x0040]
))

allowed_chr += allowed_non_leading_chr


class UnicodeField(
    CharField
):
    def __init__(self, **kwargs):
        kwargs.setdefault('max_length', 32)
        kwargs.setdefault('min_length', 1)

        self.spaces = kwargs.pop('spaces', False)
        self.numeric = kwargs.pop('numeric', True)
        super(UnicodeField, self).__init__(**kwargs)

    def run_validation(self, data=empty):
        data = super(UnicodeField, self).run_validation(data)

        if not self.numeric:
            try:
                float(data)
                raise ValidationError(_('Can not be numeric.'))
            except ValueError:
                pass

        if not self.spaces:
            if ' ' in data:
                raise ValidationError(_('Space is not supported.'))

        if data[0] in allowed_non_leading_chr:
            raise ValidationError(_('Bad leading character.'))

        for symbol in data.replace(' ', ''):
            if symbol not in allowed_chr:
                raise ValidationError(_('Unsupported character found.'))

        return data
