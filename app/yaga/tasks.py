from __future__ import absolute_import, division, unicode_literals

import datetime

from django.utils import timezone

from app import celery
from .models import Code, Group


class CodeCleanup(celery.PeriodicTask):
    run_every = datetime.timedelta(seconds=15)

    def run(self, *args, **kwargs):
        Code.objects.filter(
            expire_at__lte=timezone.now()
        ).delete()


class GroupCleanup(celery.PeriodicTask):
    run_every = datetime.timedelta(minutes=1)

    def run(self, *args, **kwargs):
        for group in Group.objects.filter(
            members=None
        ):
            group.delete()
