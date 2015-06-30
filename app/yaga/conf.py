from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import datetime
import os

import regex
from appconf import AppConf
from decouple import config
from django.conf import settings  # noqa


class YagaAppConf(
    AppConf
):
    PERIODIC_CLEANUP = True

    SMS_EXPIRATION = datetime.timedelta(minutes=5)
    SMS_TITLE = 'yaga'

    SMS_KEY = '354d4cc5'
    SMS_SECRET = '066e303e'

    SMS_DEFAULT_LANGUAGE_CODE = 'en-us'

    SLOP_FACTOR = datetime.timedelta(seconds=5)

    AWS_UPLOAD_EXPIRES = datetime.timedelta(minutes=10)
    AWS_UPLOAD_MAX_LENGTH = 25 * 1024 * 1024
    AWS_UPLOAD_MIME = 'video/mp4'

    ATTACHMENT_PREFIX = 'posts'
    ATTACHMENT_PREVIEW_PREFIX = 'posts_preview'
    ATTACHMENT_SERVER_PREVIEW_PREFIX = 'posts_server_preview'
    ATTACHMENT_TRASH_PREFIX = 'trash'

    ATTACHMENT_PREVIEW = {
        'width': 200,
        'height': 200,
        'speed': 1.5,
        'fps': 4
    }
    ATTACHMENT_VALIDATE_TIMEOUT = 60 * 3
    ATTACHMENT_VALIDATE_CMD = 'ffprobe {path}'
    ATTACHMENT_VALIDATE_RULES = (
        ('major_brand', 'mp42'),
        ('compatible_brands', 'mp41mp42isom'),
        ('Stream #0:0(und): Audio', 'aac'),
        ('Stream #0:0(und): Audio', 'mp4a'),
        ('Stream #0:1(und): Video', 'h264'),
        ('Stream #0:1(und): Video', 'avc1'),
        ('Stream #0:1(und): Video', 'yuv420p'),
        ('Stream #0:1(und): Video', '640x480'),
        ('Stream #0:1(und): Video:', 'fps')
    )

    ATTACHMENT_TRANSCODE_CMD = (
        'ffmpeg -i {input} -vf "transpose={transpose}'
        +
        ',scale={width}:-1" -r {fps} -f image2pipe -vcodec ppm - | convert -delay {speed} +dither -coalesce -layers Optimize -gravity Center -crop {width}x{height}+0+0 +repage - gif:- | gifsicle -O3 > '.format(  # noqa
            width=ATTACHMENT_PREVIEW['width'],
            height=ATTACHMENT_PREVIEW['height'],
            fps=ATTACHMENT_PREVIEW['fps'],
            speed=int(
                100
                /
                ATTACHMENT_PREVIEW['fps']
                /
                ATTACHMENT_PREVIEW['speed']
            )
        )
        +
        '{output}'
    )

    ATTACHMENT_READY_EXPIRES = datetime.timedelta(minutes=60)

    ATTACHMENT_TRANSCODE_EXPIRES = datetime.timedelta(minutes=90)
    ATTACHMENT_TRANSCODE_TIMEOUT = 20 * 60
    ATTACHMENT_TRANSCODE_DEADLINE = datetime.timedelta(hours=6)
    ATTACHMENT_TRANSCODE_RUN_EVERY = datetime.timedelta(minutes=10)

    CLEANUP_RUN_EVERY = datetime.timedelta(minutes=5)
    CODE_CLEANUP_RUN_EVERY = datetime.timedelta(seconds=15)

    AWS_SQS_QUEUE = config('AWS_SQS_QUEUE', default='yaga-dev')

    PUSH_NEW_MEMBERS_LIMIT = 3
    PUSH_BADGE = 1
    PUSH_SOUND = 'push.m4a'

    APNS_MODE = config('APNS_MODE', default='sandbox')

    APNS_FEEDBACK_MODE = 'feedback_{mode}'.format(
        mode=APNS_MODE
    )
    APNS_FEEDBACK_RUN_EVERY = datetime.timedelta(hours=12)

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

    YAGA_PUSH_POST_WINDOW = datetime.timedelta(minutes=5)

    MONKEY_LOGIN = True

    CLOUDFRONT_CLEAN_CACHE_KEY_TTL = 60 * 30
    CLOUDFRONT_CLEAN_CACHE_KEY = 'yaga:cloudfront_purge_cache_key'
    CLOUDFRONT_CLEAN_RUN_EVERY = datetime.timedelta(minutes=5)

    CLIENT_VERSION_NO_TRANSPOSE = 210
    CLIENT_VERSION_HEADER = 'HTTP_USER_AGENT'
    DEFAULT_CLIENT_HEADER = 'YAGA IOS 0.0.0'
    CLIENT_RE = regex.compile(
        r'YAGA\s(?P<vendor>IOS|ANDROID)\s(?P<version>\d+\.\d\.\d)'
    )
    SUPPORTED_CLIENT_VERSIONS = (
        lambda version: version == 0,
        lambda version: version > 210
    )

    class Meta:
        prefix = 'yaga'
