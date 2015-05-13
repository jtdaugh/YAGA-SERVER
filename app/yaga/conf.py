from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import datetime
import os

from appconf import AppConf
from decouple import config
from django.conf import settings  # noqa


class YagaAppConf(
    AppConf
):
    SMS_EXPIRATION = datetime.timedelta(minutes=5)
    SMS_TITLE = 'yaga'

    SMS_KEY = '354d4cc5'
    SMS_SECRET = '066e303e'

    SMS_DEFAULT_LANGUAGE_CODE = 'en-us'

    SLOP_FACTOR = datetime.timedelta(seconds=5)

    AWS_UPLOAD_EXPIRES = datetime.timedelta(minutes=10)
    AWS_UPLOAD_MAX_LENGTH = 25 * 1024 * 1024
    AWS_UPLOAD_MIME = 'video/mp4',
    ATTACHMENT_PREFIX = 'posts'
    ATTACHMENT_PREVIEWS = [
        {
            'x': 200,
            'y': 200,
            'speed': 1.5,
            'fps': 4
        }
    ]
    ATTACHMENT_READY_EXPIRES = datetime.timedelta(minutes=60)

    CLEANUP_RUN_EVERY = datetime.timedelta(minutes=1)

    AWS_SQS_QUEUE = config('AWS_SQS_QUEUE', default='yaga-dev')

    PUSH_POST_WINDOW = datetime.timedelta(minutes=5)
    PUSH_NEW_MEMBERS_BATCH_LIMIT = 3
    PUSH_BADGE = 1
    PUSH_SOUND = 'push.m4a'

    APNS_MODE = config('APNS_MODE', default='sandbox')

    APNS_CERT = os.path.join(
        settings.PROJECT_ROOT,
        'apns/{mode}'.format(
            mode=APNS_MODE
        )
    )

    APNS_MODE = 'push_{mode}'.format(
        mode=APNS_MODE
    )

    APNS_POOL = True
    APNS_POOL_TIMEOUT = datetime.timedelta(seconds=30)

    MONKEY_LOGIN = True

    class Meta:
        prefix = 'yaga'
