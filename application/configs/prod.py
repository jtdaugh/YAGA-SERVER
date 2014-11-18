from .base import BaseConfig


class Config(BaseConfig):
    AWS_ACCESS_KEY_ID = 'AKIAJSOKYB6HRKACSAMA'
    AWS_SECRET_ACCESS_KEY = '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'
    S3_BUCKET_NAME = 'hellysmile'
    S3_USE_HTTPS = True
    USE_S3 = True
    USE_S3_DEBUG = False
    FLASK_ASSETS_USE_S3 = True
    ASSETS_AUTO_BUILD = False
    ASSETS_CACHE = False
    ASSETS_MANIFEST = False

    CACHE_TYPE = 'simple'

    SECRET_KEY = 'SECRET_KEY'
    SECURITY_PASSWORD_SALT = 'SALT'

    DEBUG_TB_ENABLED = False
