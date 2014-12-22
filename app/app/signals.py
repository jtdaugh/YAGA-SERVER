from __future__ import absolute_import, division, unicode_literals

from django.db.models import signals


class ModelSignal(
    object
):
    model = None
    receiver = None
    signals = ['pre_save', 'post_save', 'pre_delete', 'post_delete']

    def __init__(self, *args, **kwargs):
        if self.model is None:
            raise NotImplemented('Model is not defined')

        if self.receiver is None:
            raise NotImplemented('Receiver is not defined')

    def connect(self):
        for signal in self.signals:
            _receiver = getattr(self.receiver, signal)

            _signal = getattr(signals, signal)

            _signal.connect(_receiver, sender=self.model)
