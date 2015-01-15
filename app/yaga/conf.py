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

    AWS_UPLOAD_EXPIRES = datetime.timedelta(minutes=5)
    AWS_UPLOAD_MAX_LENGTH = 25 * 1024 * 1024
    AWS_ALLOWED_MIME = 'video/quicktime'
    AWS_SQS_QUEUE = 's3_yaga-dev_sqs'

    APNS_MODE = 'push_sandbox'
    YAGA_APNS_CERT = os.path.join(
        settings.PROJECT_ROOT,
        'apns/cert_file'
    )

    class Meta:
        prefix = 'yaga'
