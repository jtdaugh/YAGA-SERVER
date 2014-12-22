from __future__ import absolute_import, division, unicode_literals

import datetime

from django.utils import timezone

from app import celery
from .models import Code


class CodeCleanup(celery.PeriodicTask):
    run_every = datetime.timedelta(seconds=15)

    def run(self, *args, **kwargs):
        Code.objects.filter(
            expire_at__lte=timezone.now()
        ).delete()
