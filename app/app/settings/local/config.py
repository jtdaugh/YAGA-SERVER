from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from ..base.config import BaseConfiguration, Implementation, Initialization


class LocalConfiguration(
    BaseConfiguration
):
    # -------------------------------------------------------
    # cache configuration
    # -------------------------------------------------------
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://localhost:6379/2',
            'OPTIONS': {
                'PICKLE_VERSION': 2,
                'IGNORE_EXCEPTIONS': True
            }
        }
    }


class LocalImplementation(
    Implementation
):
    pass


class Configuration(
    Initialization,
    LocalConfiguration,
    LocalImplementation
):
    pass
