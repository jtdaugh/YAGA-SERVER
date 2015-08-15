from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import django_filters
from django.db import models

from app.filters import UUIDFilter, empty_choice, icontains
from app.model_fields import UUIDField

from ...models import Post


class PostFilterSet(
    django_filters.FilterSet
):
    filter_overrides = {
        UUIDField: icontains,
        models.CharField: icontains,
        models.ForeignKey: {
            'filter_class': UUIDFilter,
            'extra': lambda f: {
                'lookup_type': 'exact',
            }
        }
    }

    state = django_filters.ChoiceFilter(
        choices=empty_choice + tuple(Post.state_choices)
    )

    approve_state = django_filters.ChoiceFilter(
        choices=empty_choice + tuple(Post.approval_choices)
    )

    class Meta:
        model = Post
        fields = ['id', 'user', 'group', 'name', 'state', 'approve_state']
