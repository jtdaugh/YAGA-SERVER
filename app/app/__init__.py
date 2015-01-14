from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from manage import setup

setup()

from configurations import importer

importer.install()

from celery import Celery
from celery.task import PeriodicTask
from django.conf import settings
from django.db import transaction


celery = Celery(__name__)


class AtomicTask(
    celery.Task
):
    abstract = True

    def __call__(self, *args, **kwargs):
        with transaction.atomic():
            return super(AtomicTask, self).__call__(
                *args, **kwargs
            )


class AtomicPeriodicTask(
    PeriodicTask
):
    abstract = True

    def __call__(self, *args, **kwargs):
        with transaction.atomic():
            return super(AtomicPeriodicTask, self).__call__(
                *args, **kwargs
            )


celery.AtomicTask = AtomicTask
celery.AtomicPeriodicTask = AtomicPeriodicTask
celery.PeriodicTask = PeriodicTask


celery.config_from_object('django.conf:settings')
celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
