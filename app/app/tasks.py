from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import datetime
import logging
from urllib.parse import urljoin

from . import celery
from .utils import get_requests_session
from .conf import settings


logger = logging.getLogger(__name__)


class SelfHeartBeat(
    celery.PeriodicTask
):
    run_every = datetime.timedelta(minutes=5)

    def run(self, *args, **kwargs):
        if not settings.DEBUG:
            session = get_requests_session()

            host = settings.SESSION_COOKIE_DOMAIN

            if settings.HTTPS:
                schema = 'https://'
            else:
                schema = 'http://'

            url = urljoin(schema, host)

            try:
                session.get(url)
            except Exception as e:
                logging.exception(e)
