from __future__ import absolute_import, division, unicode_literals

import json
import logging
from urllib import urlencode

from django.conf import settings

from app.utils import create_requests_session


logger = logging.getLogger(__name__)


class NexmoResponse(object):
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


class NexmoProvider(object):
    FORMAT = 'json'
    VERIFY_ENDPOINT = 'https://1api.nexmo.com/verify/'
    SEND_VERIFY_ENDPOINT = VERIFY_ENDPOINT + FORMAT
    CHECK_VERIFY_ENDPOINT = VERIFY_ENDPOINT + 'check/' + FORMAT

    session = create_requests_session()

    @property
    def api_key(self):
        return settings.CONSTANTS.SMS_KEY

    @property
    def api_secret(self):
        return settings.CONSTANTS.SMS_SECRET

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
            logger.error(e)

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
            'brand': settings.CONSTANTS.SMS_TITLE,
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
