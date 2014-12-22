from __future__ import absolute_import, division, unicode_literals

from urllib.parse import urlencode

from flask import json

from ..utils import get_http_session, get_locale_string
from .base import BaseStorage


class AbstractProvider(object):
    def __init__(self, app):
        self.app = app

    def send_message(self, receiver, message, sender=None):
        raise NotImplementedError

    def send_verify(self, receiver, message=None, sender=None, locale=None):
        raise NotImplementedError

    def check_verify(self, request_id, code, ip=None):
        raise NotImplementedError


class NexmoProvider(AbstractProvider):
    FORMAT = 'json'
    VERIFY_ENDPOINT = 'https://api.nexmo.com/verify/'
    SEND_VERIFY_ENDPOINT = VERIFY_ENDPOINT + FORMAT
    CHECK_VERIFY_ENDPOINT = VERIFY_ENDPOINT + 'check/' + FORMAT

    @property
    def api_key(self):
        return self.app.config['SMS_KEY']

    @property
    def api_secret(self):
        return self.app.config['SMS_SECRET']

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

    def request(self, url, params, method='GET'):
        try:
            method = getattr(self.session, method.lower())

            response = method(self.format_request(url, params))

            self.app.logger.info(response.text)

            return self.parse(response.text)
        except Exception as e:
            self.app.logger.error(e)

            return None

    def parse(self, text):
        return json.loads(text)

    def send_verify(
        self, receiver,
        message=None, sender=None, locale=None, length=None
    ):
        params = {
            'number': int(receiver),
            'brand': self.app.config['SMS_BRAND'],
        }

        if sender is None:
            sender = self.app.config['SMS_SENDER']

        if sender is not None:
            params['sender_id'] = sender

        if locale is not None:
            params['lg'] = get_locale_string(locale).replace('_', '-')

        if length is not None:
            params['code_length'] = length

        response = self.request(
            self.SEND_VERIFY_ENDPOINT,
            params
        )

        if (
            response
            and
            isinstance(response, dict)
            and
            response.get('request_id')
        ):
            return response['request_id']

        return None

    def check_verify(
        self, request_id, code,
        ip=None
    ):
        params = {
            'request_id': request_id,
            'code': code
        }

        if ip is not None:
            params['ip'] = ip

        response = self.request(
            self.CHECK_VERIFY_ENDPOINT,
            params
        )

        if response and not response.get('error_text'):
            return True

        return False


class Phone(BaseStorage):
    PROVIDER = NexmoProvider

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        provider = self.PROVIDER(app)

        provider.session = get_http_session(app)

        self.merge(provider)
