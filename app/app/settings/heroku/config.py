from __future__ import absolute_import, division, unicode_literals

import os

import dj_database_url
from memcacheify import memcacheify

from app.settings.base.config import (
    BaseConfiguration, Implementation, Initialization
)


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
    USE_ETAGS = True
    # -------------------------------------------------------
    # gzip configuration
    # -------------------------------------------------------
    GZIP = True
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
        '*'
    ]
    USE_X_FORWARDED_HOST = True
    BEHIND_PROXY = True
    # -------------------------------------------------------
    # database configuration
    # -------------------------------------------------------
    DATABASES = {}
    DATABASES['default'] = dj_database_url.config()
    DATABASES['default'].update({
        'ENGINE': 'transaction_hooks.backends.postgresql_psycopg2',
        'ATOMIC_REQUESTS': True,
        'AUTOCOMMIT': True,
        'CONN_MAX_AGE': 30
    })
    # -------------------------------------------------------
    # cache configuration
    # -------------------------------------------------------
    CACHES = memcacheify()
    # -------------------------------------------------------
    # sessions\message configuration
    # -------------------------------------------------------
    SESSION_REDIS_ENV_URLS = ['REDISCLOUD_URL']
    SESSION_ENGINE = 'redis_sessions_fork.session'
    # -------------------------------------------------------
    # cookies configuration
    # -------------------------------------------------------
    SESSION_COOKIE_DOMAIN = None
    CSRF_COOKIE_DOMAIN = None
    # -------------------------------------------------------
    # email backend configuration
    # -------------------------------------------------------
    EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
    EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    SERVER_EMAIL = 'root@127.0.0.1'
    DEFAULT_FROM_EMAIL = SERVER_EMAIL
    # -------------------------------------------------------
    # celery configuration
    # -------------------------------------------------------
    CELERY_ALWAYS_EAGER = False
    BROKER_URL = os.environ['RABBITMQ_BIGWIG_URL']
    CELERYD_LOG_LEVEL = 'INFO'
    CELERY_RESULT_BACKEND = os.environ['RABBITMQ_BIGWIG_URL']
    # BROKER_POOL_LIMIT = 1
    # -------------------------------------------------------
    # model auto registration configuration
    # -------------------------------------------------------
    MODELS_AUTO_REGISTRATION = False
    # -------------------------------------------------------
    # storages configuration
    # -------------------------------------------------------
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
    DEFAULT_FILE_STORAGE = 'app.storage.S3MediaStorage'
    S3_HOST = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
    MEDIA_URL = '%smedia/' % S3_HOST
    STATICFILES_STORAGE = 'app.storage.CachedS3StaticStorage'
    STATIC_URL = '%sstatic/' % S3_HOST
    COMPRESS_STORAGE = 'app.storage.CachedS3StaticStorage'
    COMPRESS_URL = STATIC_URL


class HerokuImplementation(
    Implementation
):
    def implement(self):
        super(HerokuImplementation, self).implement()
        # -------------------------------------------------------
        # collectfast implementation
        # -------------------------------------------------------
        self.INSTALLED_APPS.append('collectfast')

    def connect(self):
        pass


class Configuration(
    Initialization,
    HerokuImplementation,
    HerokuConfiguration
):
    pass
