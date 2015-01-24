from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.utils import timezone
from django.utils.functional import SimpleLazyObject

from .conf import settings


def environment(request):
    def _now():
        return timezone.now()

    def _settings():
        return settings

    return {
        'now': SimpleLazyObject(_now),
        'favicon': settings.FAVICON_STATIC,
        'settings': SimpleLazyObject(_settings)
    }
