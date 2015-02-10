from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from manage import setup  # noqa

setup()

from configurations import importer  # noqa

importer.install()

from celery import Celery  # noqa
from celery.task import PeriodicTask  # noqa
from django.db import transaction  # noqa

from .conf import settings  # noqa


default_app_config = 'app.apps.AppAppConfig'


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


def autodiscover_tasks():
    return settings.INSTALLED_APPS

celery.config_from_object('django.conf:settings')
celery.autodiscover_tasks(autodiscover_tasks)
