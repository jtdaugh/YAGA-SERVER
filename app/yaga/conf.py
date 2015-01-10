from __future__ import absolute_import, division, unicode_literals

import datetime

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
    AWS_UPLOAD_LENGTH = 25 * 1024 * 1024
    SQS_QUEUE = 's3_yaga-dev_sqs'

    class Meta:
        prefix = 'yaga'
