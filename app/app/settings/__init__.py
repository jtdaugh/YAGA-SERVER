from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import os


if os.environ.get('DYNO'):
    from .heroku import config as settings
elif os.environ.get('TRAVIS'):
    from .travis import config as settings
else:
    from .local import config as settings


Configuration = settings.Configuration
