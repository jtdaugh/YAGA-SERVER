from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import django_filters

icontains = {
    'filter_class': django_filters.CharFilter,
    'extra': lambda x: {
        'lookup_type': 'icontains',
    }
}
