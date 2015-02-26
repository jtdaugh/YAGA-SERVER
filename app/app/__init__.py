from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from manage import setup  # noqa

from .celery_app import celery  # noqa

default_app_config = 'app.apps.AppAppConfig'
