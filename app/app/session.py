from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import base64

from django.utils.module_loading import import_by_path

from .conf import settings
from .utils import force_bytes

SessionBase = import_by_path('{path}.SessionStore'.format(
    path=settings.REAL_SESSION_ENGINE
))


class SessionStore(
    SessionBase
):
    def encode(self, session_dict):
        serialized = self.serializer().dumps(session_dict)
        return base64.b64encode(serialized).decode('ascii')

    def decode(self, session_data):
        serialized = base64.b64decode(force_bytes(session_data))

        return self.serializer().loads(serialized)
