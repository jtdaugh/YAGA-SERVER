from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from configurations.wsgi import get_wsgi_application
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.wsgi import SharedDataMiddleware

from manage import setup

from .conf import settings

setup()


application = get_wsgi_application()


if settings.HANDLE_STATIC:
    application = SharedDataMiddleware(application, {
        settings.MEDIA_URL: settings.MEDIA_ROOT,
        settings.STATIC_URL: settings.STATIC_ROOT,
    })


if settings.BEHIND_PROXY:
    application = ProxyFix(application)
