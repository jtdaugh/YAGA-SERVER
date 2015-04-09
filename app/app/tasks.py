from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import datetime
import logging
from urllib.parse import urljoin

from . import celery
from .conf import settings
from .utils import get_requests_session

logger = logging.getLogger(__name__)


if not settings.DEBUG:
    class SelfHeartBeat(
        celery.PeriodicTask
    ):
        run_every = datetime.timedelta(minutes=5)

        def run(self, *args, **kwargs):
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
