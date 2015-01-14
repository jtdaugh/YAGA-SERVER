from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from rest_framework.authentication import \
    TokenAuthentication as BaseTokenAuthentication

from .models import Token


class TokenAuthentication(
    BaseTokenAuthentication
):
    model = Token
