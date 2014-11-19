from __future__ import absolute_import, division, unicode_literals
from future import standard_library
standard_library.install_aliases()

from os import environ
from urlparse import urlparse

from .base import BaseConfig


class Config(BaseConfig):
    AWS_ACCESS_KEY_ID = environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = environ['AWS_SECRET_ACCESS_KEY']
    S3_BUCKET_NAME = environ['S3_BUCKET_NAME']
    S3_BUCKET_NAME_MEDIA = environ['S3_BUCKET_NAME_MEDIA']
    S3_USE_HTTPS = True
    USE_S3 = True

    FLASK_ASSETS_USE_S3 = True
    ASSETS_AUTO_BUILD = False
    ASSETS_CACHE = False
    ASSETS_MANIFEST = False
    ASSETS_VERSIONS = False
    ASSETS_URL_EXPIRE = False

    SECRET_KEY = environ['SECRET_KEY']
    SECURITY_PASSWORD_SALT = environ['SECURITY_PASSWORD_SALT']

    CACHE_TYPE = 'saslmemcached'
    CACHE_MEMCACHED_SERVERS = [environ['MEMCACHIER_SERVERS']]
    CACHE_MEMCACHED_USERNAME = environ['MEMCACHIER_USERNAME']
    CACHE_MEMCACHED_PASSWORD = environ['MEMCACHIER_PASSWORD']

    SQLALCHEMY_DATABASE_URI = environ['DATABASE_URL']

    CELERY_BROKER_URL = environ['RABBITMQ_BIGWIG_URL']
    CELERY_RESULT_BACKEND = environ['RABBITMQ_BIGWIG_URL']

    SENTRY_DSN = environ['SENTRY_DSN']

    redis_url = environ.get('REDISCLOUD_URL')
    redis_url = urlparse(redis_url)
    REDIS_HOST = redis_url.hostname
    REDIS_PORT = redis_url.port
    REDIS_PASSWORD = redis_url.password

    DEBUG_TB_ENABLED = False
