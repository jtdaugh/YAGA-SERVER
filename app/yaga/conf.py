from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import datetime
import os

from appconf import AppConf
from django.conf import settings  # noqa


class YagaAppConf(
    AppConf
):
    SMS_EXPIRATION = datetime.timedelta(minutes=5)
    SMS_TITLE = 'yaga'

    SMS_KEY = '354d4cc5'
    SMS_SECRET = '066e303e'

    SLOP_FACTOR = datetime.timedelta(seconds=5)

    AWS_UPLOAD_EXPIRES = datetime.timedelta(minutes=10)
    AWS_UPLOAD_MAX_LENGTH = 25 * 1024 * 1024
    AWS_ALLOWED_MIME = {
        'attachment': 'video/mp4',
        'attachment_preview': 'image/gif'
    }
    ATTACHMENT_PREVIEW_PREFIX = 'posts_preview'
    ATTACHMENT_PREFIX = 'posts'
    ATTACHMENT_PREVIEW_SIZE = [
        {
            'x': 240,
            'y': 240
        },
        {
            'x': 200,
            'y': 200
        },
        {
            'x': 240,
            'y': 200
        },
        {
            'x': 200,
            'y': 240
        }
    ]
    ATTACHMENT_READY_EXPIRES = datetime.timedelta(minutes=60)

    CLEANUP_RUN_EVERY = datetime.timedelta(minutes=1)

    AWS_SQS_QUEUE = os.environ.get('AWS_SQS_QUEUE', 'yaga-dev')

    PUSH_POST_WINDOW = datetime.timedelta(minutes=5)
    PUSH_NEW_MEMBERS_BATCH_LIMIT = 3
    PUSH_BADGE = 1
    PUSH_SOUND = 'push.m4a'

    APNS_MODE = os.environ.get('APNS_MODE', 'sandbox')

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
