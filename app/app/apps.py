from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AppAppConfig(
    AppConfig
):
    name = 'app'
    verbose_name = _('App')

    def ready(self):
        from . import dispatch  # noqa # isort:skip
