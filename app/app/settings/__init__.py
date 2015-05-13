from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import os

from decouple import config
from django.utils.module_loading import import_by_path

if os.environ.get('DYNO'):
    os.environ['ENV'] = 'heroku'
elif os.environ.get('TRAVIS'):
    os.environ['ENV'] = 'travis'

ENV = config('ENV', default='local')

Configuration = import_by_path(
    'app.settings.{env}.config.Configuration'.format(
        env=ENV,
    )
)
