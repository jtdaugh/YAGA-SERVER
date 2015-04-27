from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib.auth import get_user_model

from app.signals import ModelSignal

from .receivers import UserReceiver


class UserSignal(
    ModelSignal
):
    model = get_user_model()
    receiver = UserReceiver
