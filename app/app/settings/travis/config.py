from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import dj_database_url

from ..base.config import BaseConfiguration, Implementation, Initialization


# import psycopg2.extensions


class TravisConfiguration(
    BaseConfiguration
):
    # -------------------------------------------------------
    # debug mode configuration
    # -------------------------------------------------------
    DEBUG = True
    # -------------------------------------------------------
    # https configuration
    # -------------------------------------------------------
    HTTPS = False
    # -------------------------------------------------------
    # django compressor configuration
    # -------------------------------------------------------
    COMPRESS_OFFLINE = True
    COMPRESS_ENABLED = False
    # -------------------------------------------------------
    # template cache configuration
    # -------------------------------------------------------
    TEMPLATE_CACHE = False
    # -------------------------------------------------------
    # etag configuration
    # -------------------------------------------------------
    USE_ETAGS = False
    # -------------------------------------------------------
    # gzip configuration
    # -------------------------------------------------------
    GZIP = False
    # -------------------------------------------------------
    # debug toolbar configuration
    # -------------------------------------------------------
    DEBUG_TOOLBAR = False
    # -------------------------------------------------------
    # docs configuration
    # -------------------------------------------------------
    USE_DOCS = False
    # -------------------------------------------------------
    # crispy forms configuration
    # -------------------------------------------------------
    CRISPY_FAIL_SILENTLY = False
    # -------------------------------------------------------
    # local cache configuration
    # -------------------------------------------------------
    VIEW_CACHE = False
    # -------------------------------------------------------
    # hosts configuration
    # -------------------------------------------------------
    ALLOWED_HOSTS = [
        '*'
    ]
    USE_X_FORWARDED_HOST = True
    BEHIND_PROXY = False
    # -------------------------------------------------------
    # database configuration
    # -------------------------------------------------------
    DATABASES = {}
    DATABASES['default'] = dj_database_url.parse(
        'postgresql://:@127.0.0.1:5432/app'
    )
    DATABASES['default'].update({
        'ENGINE': 'transaction_hooks.backends.postgresql_psycopg2',
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 30,
        'AUTOCOMMIT': True,
        # 'OPTIONS': {
        #     'isolation_level': psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ  # noqa
        # }
    })
    # -------------------------------------------------------
    # cache configuration
    # -------------------------------------------------------
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
            'LOCATION': '127.0.0.1:11211'
        }
    }
    # -------------------------------------------------------
    # sessions\message configuration
    # -------------------------------------------------------
    SESSION_REDIS_ENV_URLS = []
    SESSION_REDIS_HOST = '127.0.0.1'
    SESSION_REDIS_PORT = 6379
    SESSION_REDIS_DB = 3
    SESSION_REDIS_PASSWORD = None
    SESSION_REDIS_PREFIX = None
    REAL_SESSION_ENGINE = 'redis_sessions_fork.session'
    # -------------------------------------------------------
    # cookies configuration
    # -------------------------------------------------------
    SESSION_COOKIE_DOMAIN = None
    CSRF_COOKIE_DOMAIN = None
    # -------------------------------------------------------
    # celery configuration
    # -------------------------------------------------------
    CELERY_ALWAYS_EAGER = False
    BROKER_URL = 'amqp://guest:guest@localhost:5672//'
    CELERYD_LOG_LEVEL = 'INFO'
    CELERY_RESULT_BACKEND = 'amqp://guest:guest@localhost:5672//'
    # BROKER_POOL_LIMIT = 1
    # -------------------------------------------------------
    # model auto registration configuration
    # -------------------------------------------------------
    MODELS_AUTO_REGISTRATION = False


class TravisImplementation(
    Implementation
):
    pass


class Configuration(
    Initialization,
    TravisConfiguration,
    TravisImplementation
):
    pass
