from __future__ import absolute_import, division, unicode_literals

from functools import wraps

from rest_framework.throttling import ScopedRateThrottle

from app.utils import smart_text


def set_scope(fn):
    @wraps(fn)
    def wrapper(cls, request, view):
        setattr(view, cls.scope_attr, smart_text(cls.__class__.__name__))

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
