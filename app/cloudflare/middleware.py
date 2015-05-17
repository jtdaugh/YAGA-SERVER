from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from werkzeug.contrib.fixers import ProxyFix

from .conf import settings
from .utils import cloudflare_mask


class CloudFlareProxyFix(
    ProxyFix
):
    def get_remote_addr(self, forwarded_for):
        if forwarded_for:
            remote_addr = forwarded_for[-1]

            return remote_addr


class CloudFlareFix(
    object
):
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        if settings.CLOUDFLARE_BEHIND:
            cf_connecting_ip = environ.get('HTTP_CF_CONNECTING_IP', None)

            environ['CF_FORBIDDEN'] = False

            if not cloudflare_mask.is_valid_remote_addr(cf_connecting_ip):
                environ['CF_FORBIDDEN'] = True
            elif cloudflare_mask.is_cloudflare(environ['REMOTE_ADDR']):
                environ['REMOTE_ADDR'] = cf_connecting_ip
            else:
                environ['CF_FORBIDDEN'] = True

        return self.application(environ, start_response)


class CloudFlareMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if settings.CLOUDFLARE_BEHIND:
            if request.META.get('CF_FORBIDDEN') is None:
                raise ImproperlyConfigured(
                    'Missing CloudFlareFix at wsgi:application'
                )

            if request.META['CF_FORBIDDEN']:
                raise SuspiciousOperation('Cloudflare security runtime error.')
