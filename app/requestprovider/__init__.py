from __future__ import absolute_import, division, unicode_literals

from django.core.exceptions import ImproperlyConfigured

from .signals import request_provider


def get_request():
    try:
        return request_provider.send_robust(None)[0][1]
    except IndexError:
        raise ImproperlyConfigured
