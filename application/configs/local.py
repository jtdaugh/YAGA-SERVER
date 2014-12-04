from __future__ import absolute_import, division, unicode_literals

from .base import BaseConfig


class Config(BaseConfig):
    DEBUG = True

    AWS_ACCESS_KEY_ID = 'AKIAJSOKYB6HRKACSAMA'
    AWS_SECRET_ACCESS_KEY = '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'
    S3_BUCKET_NAME = 'yaga-dev-static'
    S3_BUCKET_NAME_MEDIA = 'yaga-dev-media'
    S3_USE_HTTPS = False
    USE_S3 = False

    FLASK_ASSETS_USE_S3 = False
    ASSETS_AUTO_BUILD = True
    ASSETS_CACHE = False
    ASSETS_MANIFEST = False
    ASSETS_VERSIONS = 'hash'
    ASSETS_URL_EXPIRE = True

    SECRET_KEY = 'SECRET_KEY'
    SECURITY_PASSWORD_SALT = 'SALT'

    CACHE_TYPE = 'memcached'

    SQLALCHEMY_DATABASE_URI = 'postgresql://:@127.0.0.1:5432/yaga_dev'

    CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
    CELERY_RESULT_BACKEND = 'amqp://guest:guest@localhost:5672//'

    APP_HOST = '127.0.0.1'
    APP_PORT = 5000

    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    DEBUG_TB_PANELS = [
        'flask_debugtoolbar.panels.versions.VersionDebugPanel',
        'flask_debugtoolbar.panels.timer.TimerDebugPanel',
        'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
        'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        'flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel',
        'flask_debugtoolbar.panels.template.TemplateDebugPanel',
        'flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
        'flask_debugtoolbar.panels.logger.LoggingPanel',
        'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
    ]
