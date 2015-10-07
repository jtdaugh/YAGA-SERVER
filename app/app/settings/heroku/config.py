from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import dj_database_url
from decouple import config

from ..base.config import BaseConfiguration, Implementation, Initialization


# import psycopg2.extensions


class HerokuConfiguration(
    BaseConfiguration
):
    # -------------------------------------------------------
    # debug mode configuration
    # -------------------------------------------------------
    DEBUG = False
    # -------------------------------------------------------
    # https configuration
    # -------------------------------------------------------
    HTTPS = True
    # -------------------------------------------------------
    # django compressor configuration
    # -------------------------------------------------------
    COMPRESS_OFFLINE = True
    COMPRESS_ENABLED = True
    # -------------------------------------------------------
    # template cache configuration
    # -------------------------------------------------------
    TEMPLATE_CACHE = True
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
    USE_DOCS = True
    # -------------------------------------------------------
    # crispy forms configuration
    # -------------------------------------------------------
    CRISPY_FAIL_SILENTLY = True
    # -------------------------------------------------------
    # local cache configuration
    # -------------------------------------------------------
    VIEW_CACHE = True
    # -------------------------------------------------------
    # hosts configuration
    # -------------------------------------------------------
    ALLOWED_HOSTS = [
        'api.yaga.video',
        'www.yaga.video',

        'api-dev.yaga.video',
        'www-dev.yaga.video'
    ]
    USE_X_FORWARDED_HOST = False
    BEHIND_PROXY = False
    CLOUDFLARE_BEHIND = True
    # -------------------------------------------------------
    # database configuration
    # -------------------------------------------------------
    DATABASES = {}
    DATABASES['default'] = dj_database_url.config()
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
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('REDISCLOUD_URL'),
            'OPTIONS': {
                'PICKLE_VERSION': 2,
                'IGNORE_EXCEPTIONS': True
            }
        }
    }
    # -------------------------------------------------------
    # sessions\message configuration
    # -------------------------------------------------------
    SESSION_REDIS_ENV_URLS = ['REDISCLOUD_URL']
    REAL_SESSION_ENGINE = 'redis_sessions_fork.session'
    # -------------------------------------------------------
    # cookies configuration
    # -------------------------------------------------------
    SESSION_COOKIE_DOMAIN = config('DOMAIN')
    CSRF_COOKIE_DOMAIN = config('DOMAIN')
    # -------------------------------------------------------
    # email backend configuration
    # -------------------------------------------------------
    EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = config('SENDGRID_USERNAME')
    EMAIL_HOST_PASSWORD = config('SENDGRID_PASSWORD')
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    SERVER_EMAIL = 'root@127.0.0.1'
    DEFAULT_FROM_EMAIL = SERVER_EMAIL
    # -------------------------------------------------------
    # celery configuration
    # -------------------------------------------------------
    CELERY_ALWAYS_EAGER = False
    BROKER_URL = config('RABBITMQ_BIGWIG_URL')
    CELERYD_LOG_LEVEL = 'INFO'
    # CELERY_RESULT_BACKEND = config('RABBITMQ_BIGWIG_URL')
    CELERY_RESULT_BACKEND = config('REDISCLOUD_URL')
    # BROKER_POOL_LIMIT = 1
    # -------------------------------------------------------
    # model auto registration configuration
    # -------------------------------------------------------
    MODELS_AUTO_REGISTRATION = False
    # -------------------------------------------------------
    # storages configuration
    # -------------------------------------------------------
    AWS_REGION = config('AWS_REGION')
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')

    CLOUDFRONT_HOST = config('CLOUDFRONT_HOST', default='')

    STATICFILES_STORAGE = 'app.storage.CachedS3StaticStorage'
    COMPRESS_STORAGE = 'app.storage.CachedS3StaticStorage'


class HerokuImplementation(
    Implementation
):
    def implement(self):
        super(HerokuImplementation, self).implement()
        # -------------------------------------------------------
        # storages implementation
        # -------------------------------------------------------
        self.STATIC_URL = '{host}{location}/'.format(
            location=self.STATIC_LOCATION,
            host=self.S3_HOST
        )
        # -------------------------------------------------------
        # collectfast implementation
        # -------------------------------------------------------
        self.INSTALLED_APPS.append('collectfast')


class Configuration(
    Initialization,
    HerokuConfiguration,
    HerokuImplementation,
):
    pass
