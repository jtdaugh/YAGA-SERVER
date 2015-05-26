from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import uuid

import django_filters
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from requestprovider import get_request

icontains = {
    'filter_class': django_filters.CharFilter,
    'extra': lambda x: {
        'lookup_type': 'icontains',
    }
}

empty_choice = (('', '---------'),)


class UUIDFilter(
    django_filters.CharFilter
):
    def filter(self, qs, value, request=None):  # noqa
        if isinstance(value, django_filters.fields.Lookup):
            value = value.value

        if value:
            try:
                uuid.UUID(value)
            except ValueError:
                request = get_request()

                messages.add_message(
                    request,
                    messages.WARNING,
                    _('{value} is not valid UUID.').format(
                        value=value
                    )
                )

                return qs

        return super(UUIDFilter, self).filter(qs, value)
