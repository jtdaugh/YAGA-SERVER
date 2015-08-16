from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import django_filters
from django.db import models

from app.filters import icontains
from app.model_fields import UUIDField

from ...models import Group


class GroupFilterSet(
    django_filters.FilterSet
):
    filter_overrides = {
        UUIDField: icontains,
        models.CharField: icontains
    }

    class Meta:
        model = Group
        fields = ['id', 'name', 'private', 'featured']
