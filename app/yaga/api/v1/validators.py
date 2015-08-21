from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from ...models import Group


class UniqueLowerUserName(
    object
):
    def __call__(self, value):
        if get_user_model().objects.filter(
            name__iexact=value
        ).exists():
            raise ValidationError('This name is already taken.')


class UniqueLowerGroupName(
    object
):
    def __call__(self, value):
        if Group.objects.filter(
            name__iexact=value
        ).exists():
            raise ValidationError('Channel name already taken.')
