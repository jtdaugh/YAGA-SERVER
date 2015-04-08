from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import django
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_models
from django.db.models.signals import post_migrate

from .model_permissions import register_global_permission
from .receivers import ModelReceiver
from .signals import ModelSignal, register
from .utils import Bridge, update_permissions


def receiver_factory():
    class BridgeModelReceiver(
        ModelReceiver
    ):
        @classmethod
        def post_init(cls, sender, **kwargs):
            instance = kwargs['instance']

            if hasattr(instance, 'bridge'):
                raise ImproperlyConfigured(
                    '{model} bridge attribute is reserved'.format(
                        model=instance.__class__.__name__
                    )
                )

            instance.bridge = Bridge()

    return BridgeModelReceiver


def signal_factory(model, bridge):
    class BridgeModelSignal(
        ModelSignal
    ):
        model = model
        receiver = bridge['receiver']

    return BridgeModelSignal


bridge_storage = {}


for model in get_models():
    bridge_storage[model] = {}
    bridge_storage[model]['receiver'] = receiver_factory()
    bridge_storage[model]['signal'] = signal_factory(
        model, bridge_storage[model]
    )

    register(bridge_storage[model]['signal'])


post_migrate.connect(register_global_permission)

if django.VERSION[:2] < (1, 7):
    post_migrate.connect(update_permissions)
