from __future__ import absolute_import

from manage import setup
setup()

from django.conf import settings
from configurations.wsgi import get_wsgi_application
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.contrib.fixers import ProxyFix


application = get_wsgi_application()


if settings.HANDLE_STATIC:
    application = SharedDataMiddleware(application, {
        settings.MEDIA_URL: settings.MEDIA_ROOT,
        settings.STATIC_URL: settings.STATIC_ROOT,
    })


if settings.BEHIND_PROXY:
    application = ProxyFix(application)
