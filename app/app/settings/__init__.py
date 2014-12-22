from __future__ import absolute_import, division, unicode_literals

import os


if os.environ.get('DYNO'):
    from app.settings import heroku as settings
elif os.environ.get('TRAVIS'):
    from app.settings import travis as settings
else:
    from app.settings import local as settings


Configuration = settings.Configuration
