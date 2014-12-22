from __future__ import absolute_import, division, unicode_literals

from rest_framework.authentication import TokenAuthentication \
    as BaseTokenAuthentication

from .models import Token


class TokenAuthentication(BaseTokenAuthentication):
    model = Token
