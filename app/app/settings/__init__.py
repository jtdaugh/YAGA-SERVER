from __future__ import absolute_import, division, unicode_literals

import os


if os.environ.get('DYNO'):
    from app.settings.heroku import config as settings
elif os.environ.get('TRAVIS'):
    from app.settings.travis import config as settings
else:
    from app.settings.local import config as settings


Configuration = settings.Configuration
