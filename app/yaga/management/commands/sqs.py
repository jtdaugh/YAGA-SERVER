from __future__ import absolute_import, division, unicode_literals

import logging
import json

import boto
from django.conf import settings
from django.core.management.base import NoArgsCommand

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

        queue = sqs.create_queue(settings.CONSTANTS.SQS_QUEUE)

        while True:
            try:
                events = queue.get_messages()

                for event in events:
                    try:
                        data = json.loads(event.get_body())

                        logger.info(data)

                        if (
                            data['Records'][0]['eventName']
                            ==
                            'ObjectCreated:Post'
                        ):
                            key = data['Records'][0]['s3']['object']['key']

                            PostProcess.delay(
                                key
                            )

                        event.delete()
                    except Exception as e:
                        logger.error(e)
            except Exception as e:
                logger.error(e)
