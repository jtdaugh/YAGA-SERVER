from __future__ import absolute_import, division, unicode_literals

from django.conf import settings
from django.utils import timezone
from django.utils.functional import SimpleLazyObject


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
