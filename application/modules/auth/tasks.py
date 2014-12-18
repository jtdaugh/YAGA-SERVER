from __future__ import absolute_import, division, unicode_literals

import datetime

from ...helpers import celery
from .repository import session_storage, code_storage


class SessionCleanup(celery.PeriodicTask):
    run_every = datetime.timedelta(minutes=1)

    def run(self, *args, **kwargs):
        session_storage.delete_expired()


class CodeCleanup(celery.PeriodicTask):
    run_every = datetime.timedelta(minutes=1)

    def run(self, *args, **kwargs):
        code_storage.delete_expired()
