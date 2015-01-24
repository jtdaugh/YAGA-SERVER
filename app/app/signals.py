from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.db.models import signals


class ModelSignal(
    object
):
    model = None
    receiver = None
    signals = [
        'pre_init', 'post_init',
        'pre_save', 'post_save',
        'pre_delete', 'post_delete'
    ]

    @classmethod
    def connect(cls):
        instance = cls()

        for signal in instance.signals:
            receiver = getattr(instance.receiver, signal, None)

            if receiver is not None:
                model_signal = getattr(signals, signal)

                model_signal.connect(receiver, sender=instance.model)


def register(obj):
    obj.connect()
