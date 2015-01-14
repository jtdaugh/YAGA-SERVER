from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from types import MethodType

from django.contrib.sites.models import Site
from django.http import HttpRequest, SimpleCookie
from django.utils import six


def _set_cookie(
    self, key,
    value='',
    max_age=None,
    expires=None,
    path='/',
    domain=None,
    secure=False,
    httponly=False
):
    self._resp_cookies[key] = value
    self.COOKIES[key] = value
    if max_age is not None:
        self._resp_cookies[key]['max-age'] = max_age
    if expires is not None:
        self._resp_cookies[key]['expires'] = expires
    if path is not None:
        self._resp_cookies[key]['path'] = path
    if domain is not None:
        self._resp_cookies[key]['domain'] = domain
    if secure:
        self._resp_cookies[key]['secure'] = True
    if httponly:
        self._resp_cookies[key]['httponly'] = True


def _delete_cookie(self, key, path='/', domain=None):
    self.set_cookie(
        key,
        value='deleted',
        max_age=0,
        path=path,
        domain=domain,
        expires='Thu, 01-Jan-1970 00:00:00 GMT'
    )
    try:
        del self.COOKIES[key]
    except KeyError:
        pass


class RequestCookiesMiddleware(
    object
):
    def process_request(self, request):
        request._resp_cookies = SimpleCookie()

        if six.PY3:
            request.set_cookie = MethodType(
                _set_cookie, request
            )
            request.delete_cookie = MethodType(
                _delete_cookie, request
            )
        else:
            request.set_cookie = MethodType(
                _set_cookie, request, HttpRequest
            )
            request.delete_cookie = MethodType(
                _delete_cookie, request, HttpRequest
            )

    def process_response(self, request, response):
        if hasattr(request, '_resp_cookies'):
            if request._resp_cookies:
                response.cookies.update(request._resp_cookies)

        return response


class CapabilityMiddleware(
    object
):
    def process_request(self, request):
        if not hasattr(request, 'raw_post_data'):
            request.raw_post_data = request.body

        if not hasattr(request, 'site'):
            request.site = Site.objects.get_current()
