from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from celery import Celery
from celery.task import PeriodicTask
from django.db import transaction
from django.utils import six
from kombu.serialization import register
from mongoengine.django.sessions import BSONSerializer

from .conf import settings


if six.PY3:
    buffer = memoryview


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


bson_serializer = BSONSerializer()


register(
    'bson',
    bson_serializer.dumps,
    bson_serializer.loads,
    content_type='bson',
    content_encoding='binary'
)


class BSONBufferSerializer(
    BSONSerializer
):
    def loads(self, data):
        if isinstance(data, buffer):
            data = str(data).encode('ascii')

        return super(BSONBufferSerializer, self).loads(data)


bson_buffer_serializer = BSONBufferSerializer()


register(
    'bsonb',
    bson_buffer_serializer.dumps,
    bson_buffer_serializer.loads,
    content_type='bsonb',
    content_encoding='binary'
)


def autodiscover_tasks():
    return settings.INSTALLED_APPS


celery.config_from_object('django.conf:settings')
celery.autodiscover_tasks(autodiscover_tasks)
