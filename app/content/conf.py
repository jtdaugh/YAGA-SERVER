from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from appconf import AppConf
from django.conf import settings  # noqa


class ContentAppConf(
    AppConf
):
    GA_ID = 'XXXXX'

    class Meta:
        prefix = 'content'
