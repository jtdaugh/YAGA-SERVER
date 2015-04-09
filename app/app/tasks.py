from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import datetime
import logging

from . import celery
from .conf import settings
from .utils import get_requests_session, reverse_host

logger = logging.getLogger(__name__)


if not settings.DEBUG:
    class SelfHeartBeat(
        celery.PeriodicTask
    ):
        run_every = datetime.timedelta(minutes=5)

        def run(self, *args, **kwargs):
                session = get_requests_session()

                url = reverse_host('index')

                try:
                    session.get(url)
                except Exception as e:
                    logging.exception(e)
