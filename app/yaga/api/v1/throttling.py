from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from functools import wraps

from rest_framework.throttling import ScopedRateThrottle


def set_scope(fn):
    @wraps(fn)
    def wrapper(cls, request, view):
        setattr(view, cls.scope_attr, str(cls.__class__.__name__))

        return fn(cls, request, view)
    return wrapper


class BaseScopedRateThrottle(
    ScopedRateThrottle
):
    def get_rate(self):
        return self.rate

    @set_scope
    def allow_request(self, request, view):
        return super(BaseScopedRateThrottle, self).allow_request(
            request, view
        )


class CodeScopedRateThrottle(
    BaseScopedRateThrottle
):
    rate = '10/hour'


class TokenScopedRateThrottle(
    BaseScopedRateThrottle
):
    rate = '50/hour'


class UserSearchScopedRateThrottle(
    BaseScopedRateThrottle
):
    rate = '30/hour'
