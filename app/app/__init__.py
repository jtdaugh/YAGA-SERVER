from __future__ import absolute_import, division, unicode_literals

from manage import setup
setup()

from configurations import importer
importer.install()

from celery import Celery
from celery.task import PeriodicTask
from django.conf import settings
from django.db import transaction


celery = Celery('app')


TaskBase = celery.Task


class TransactionTask(TaskBase):
    abstract = True

    def __call__(self, *args, **kwargs):
        with transaction.atomic():
            return TaskBase.__call__(self, *args, **kwargs)


celery.Task = TransactionTask


class TransactionPeriodicTask(PeriodicTask):
    abstract = True

    def __call__(self, *args, **kwargs):
        with transaction.atomic():
            return PeriodicTask.__call__(self, *args, **kwargs)


celery.PeriodicTask = TransactionPeriodicTask


celery.config_from_object('django.conf:settings')
celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
