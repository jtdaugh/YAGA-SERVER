from __future__ import absolute_import, division, unicode_literals

import os
import datetime

from ..utils import b


class BaseConfig(object):
    LOCALES = ['en']
    LOCALE_MAP = {
        'en': 'en_US'
    }

    BABEL_DEFAULT_LOCALE = 'en'
    SECURITY_PASSWORD_HASH = b('bcrypt')
    WTF_CSRF_ENABLED = True
    SECURITY_DEFAULT_REMEMBER_ME = False

    ROLES = ['superuser']

    APP_HEADER = 'X-App-Version'

    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_DISABLE_RATE_LIMITS = True
    CELERY_ACKS_LATE = True
    CELERY_SEND_EVENTS = True
    BROKER_HEARTBEAT = True

    AUTH_TOKEN_LENGTH = 64
    SESSION_SID_LENGTH = 64

    SESSION_ENGINE = 'redis'

    CELERY_TIMEZONE = 'UTC'

    AUTH_HEADER_NAME = 'Auth'

    VIEW_CACHE_TIMEOUT = 60 * 60

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    GEOIP_MMDB = 'GeoLite2-City.mmdb'

    GEOIP_MMDB = os.path.join(
        BASE_DIR,
        'lib',
        GEOIP_MMDB
    )

    RATE_LIMIT = {
        'AUTH': {
            'ENABLED': True,
            'REQUESTS': 1000,
            'INTERVAL': datetime.timedelta(hours=1)
        },
        'IP': {
            'ENABLED': True,
            'REQUESTS': 10000,
            'INTERVAL': datetime.timedelta(hours=1)
        }
    }

    SMS_BRAND = 'yaga'
    SMS_SENDER = None
    SMS_KEY = '354d4cc5'
    SMS_SECRET = '066e303e'
    SMS_VERIFICATION_DELTA = datetime.timedelta(minutes=5)

    HTTP_RETRIES = 5

    CRYPT_SID = True

    def __init__(self, *args, **kwargs):
        self.configure()

    def get_secret_bytes(self, length=16):
        if len(self.SECRET_KEY) >= length:
            return self.SECRET_KEY[:length]

        return (
            self.SECRET_KEY * (length // len(self.SECRET_KEY) + 1)
        )[:length]

    def configure(self):
        self.CRYPT_KEY = b(self.get_secret_bytes(32)[::-1])
        self.CRYPT_IV = b(self.get_secret_bytes(16))
