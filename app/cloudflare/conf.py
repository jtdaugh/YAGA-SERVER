from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import datetime

from appconf import AppConf
from django.conf import settings  # noqa


class CloudFlareAppConf(
    AppConf
):
    ENDPOINT = 'https://www.cloudflare.com/ips-v4'
    LOAD_RUN_EVERY = datetime.timedelta(minutes=10)
    BEHIND = False

    class Meta:
        prefix = 'cloudflare'
