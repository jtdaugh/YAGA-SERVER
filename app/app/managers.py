from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.db import models


class AtomicManager(
    models.Manager
):
    def get_queryset(self):
        return super(AtomicManager, self).get_queryset().select_for_update()
