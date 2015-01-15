from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import json
import logging
from urllib.parse import urlencode

from app.utils import get_requests_session

from .conf import settings

logger = logging.getLogger(__name__)


class NexmoResponse(
    object
):
    def __init__(self, response):
        self.response = response

    def is_valid(self):
        if self.response:
            if self.response.get('status') == '0':
                return True

        return False

    def exceeded(self):
        if self.response:
            if self.response.get('status') == '17':
                return True

        return False

    @property
    def request_id(self):
        if self.response:
            if self.response.get('request_id'):
                return self.response['request_id']

        return False


class NexmoProvider(
    object
):
    FORMAT = 'json'
    VERIFY_ENDPOINT = 'https://api.nexmo.com/verify/'
    SEND_VERIFY_ENDPOINT = VERIFY_ENDPOINT + FORMAT
    CHECK_VERIFY_ENDPOINT = VERIFY_ENDPOINT + 'check/' + FORMAT

    session = get_requests_session()

    @property
    def api_key(self):
        return settings.YAGA_SMS_KEY

    @property
    def api_secret(self):
        return settings.YAGA_SMS_SECRET

    @property
    def auth_credentials(self):
        return {
            'api_key': self.api_key,
            'api_secret': self.api_secret
        }

    def format_request(self, url, params):
        params.update(self.auth_credentials)

        return '{url}?{params}'.format(
            url=url,
            params=urlencode(params)
        )

    def validate(self, data):
        if (
            data
            and
            isinstance(data, dict)
        ):
            return data
        else:
            return None

    def request(self, url, params):
        try:
            response = self.session.get(self.format_request(url, params))

            data = self.validate(self.parse(response))

            logger.info(data)
        except Exception as e:
            logger.exception(e)

            data = None

        return NexmoResponse(data)

    def parse(self, response):
        return json.loads(response.text)

    def verify(
        self, receiver,
        sender=None, locale=None, length=None
    ):
        params = {
            'number': int(receiver),
            'brand': settings.YAGA_SMS_TITLE,
        }

        if sender is not None:
            params['sender_id'] = sender

        if length is not None:
            params['code_length'] = length

        if locale is not None:
            params['lg'] = locale

        return self.request(
            self.SEND_VERIFY_ENDPOINT,
            params
        )

    def check(
        self, request_id, code,
        ip=None
    ):
        params = {
            'request_id': request_id,
            'code': code
        }

        if ip is not None:
            params['ip'] = ip

        return self.request(
            self.CHECK_VERIFY_ENDPOINT,
            params
        )


class APNSProvider(
    object
):
    def __init__(self):
        from apnsclient import Session, APNs, Message

        self.session = Session()
        self.connection = self.session.get_connection(
            settings.YAGA_APNS_MODE, cert_file=settings.YAGA_APNS_CERT
        )
        self.service = APNs(self.connection)

        self.Message = Message

    def push(self, receivers, **kwargs):
        if not isinstance(receivers, (list, tuple)):
            receivers = (receivers,)

        message = self.Message(
            receivers,
            **kwargs
        )

        response = self.service.send(message)

        return response
