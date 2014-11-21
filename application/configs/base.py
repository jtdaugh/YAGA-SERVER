from __future__ import absolute_import, division, unicode_literals

from ..utils import b


class BaseConfig(object):
    LOCALES = ['en']
    BABEL_DEFAULT_LOCALE = 'en'
    SECURITY_PASSWORD_HASH = b('bcrypt')
    WTF_CSRF_ENABLED = False
    SECURITY_DEFAULT_REMEMBER_ME = True

    ROLES = ['superuser']

    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_DISABLE_RATE_LIMITS = True
    CELERY_ACKS_LATE = True
    CELERY_SEND_EVENTS = True
    BROKER_HEARTBEAT = True
