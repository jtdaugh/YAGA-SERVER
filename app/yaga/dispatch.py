from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from app.signals import register

from . import signals

register(signals.CodeSignal)
register(signals.ContactSignal)
register(signals.DeviceSignal)
register(signals.MonkeyUserSignal)
register(signals.GroupSignal)
register(signals.MemberSignal)
register(signals.PostSignal)
register(signals.LikeSignal)
register(signals.PostCopySignal)
register(signals.UserSignal)
