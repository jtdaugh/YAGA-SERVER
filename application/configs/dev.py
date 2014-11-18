from .base import BaseConfig


class Config(BaseConfig):
    AWS_ACCESS_KEY_ID = 'AKIAJSOKYB6HRKACSAMA'
    AWS_SECRET_ACCESS_KEY = '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'
    S3_BUCKET_NAME = 'hellysmile'
    S3_USE_HTTPS = False
    USE_S3 = False

    FLASK_ASSETS_USE_S3 = False
    ASSETS_AUTO_BUILD = True
    ASSETS_CACHE = True
    ASSETS_MANIFEST = False
    ASSETS_VERSION = True
    ASSETS_URL_EXPIRE = True

    SECRET_KEY = 'SECRET_KEY'
    SECURITY_PASSWORD_SALT = 'SALT'

    CACHE_TYPE = 'filesystem'
    CACHE_DIR = 'cache'

    SQLALCHEMY_DATABASE_URI = 'postgresql://hell:@127.0.0.1:5432/yaga'

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
        'flask.ext.mongoengine.panels.MongoDebugPanel'
    ]
