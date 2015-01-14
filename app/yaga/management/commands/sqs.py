from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import json
import logging

import boto
from django.core.management.base import NoArgsCommand

from ...conf import settings
from ...tasks import PostProcess

logger = logging.getLogger(__name__)


class Command(
    NoArgsCommand
):
    help = 'SQS S3 events notifications.'

    def handle_noargs(self, **options):
        sqs = boto.connect_sqs(
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY
        )

        queue = sqs.create_queue(settings.YAGA_AWS_SQS_QUEUE)

        while True:
            try:
                events = queue.get_messages()

                for event in events:
                    try:
                        data = json.loads(event.get_body())

                        logger.info(data)

                        if data.get('Records'):
                            if (
                                data['Records'][0]['eventName']
                                ==
                                'ObjectCreated:Post'
                            ):
                                key = data['Records'][0]['s3']['object']['key']

                                if key.startswith(settings.MEDIA_LOCATION):
                                    PostProcess().delay(
                                        key
                                    )

                        event.delete()
                    except Exception as e:
                        logger.exception(e)
            except Exception as e:
                logger.exception(e)
