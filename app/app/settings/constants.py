from __future__ import absolute_import, division, unicode_literals

import datetime


class Constants(
    object
):
    GA_ID = 'XXXXX'

    SMS_EXPIRATION = datetime.timedelta(minutes=5)
    SMS_TITLE = 'yaga'
    SMS_KEY = '354d4cc5'
    SMS_SECRET = '066e303e'

    AWS_UPLOAD_EXPIRES = datetime.timedelta(minutes=5)
    AWS_UPLOAD_LENGTH = 25 * 1024 * 1024

    AWS_ACCESS_KEY_ID = 'AKIAJSOKYB6HRKACSAMA'
    AWS_SECRET_ACCESS_KEY = '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'
    AWS_STORAGE_BUCKET_NAME = 'yaga-dev'
