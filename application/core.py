from __future__ import absolute_import, division, unicode_literals

from .loader import create_app


app, celery = create_app()
