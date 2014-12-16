from __future__ import absolute_import, division, unicode_literals

from urllib.parse import urlencode

from flask import json

from .base import BaseStorage
from ..utils import get_http_session


class AbstractProvider(object):
    def __init__(self, config):
        self.config = config

    def send_message(self, receiver, message, sender=None):
        raise NotImplementedError

    def send_verify(self, receiver, message=None, sender=None, locale=None):
        raise NotImplementedError

    def check_verify(self, request, code, ip=None):
        raise NotImplementedError


class NexmoProvider(AbstractProvider):
    FORMAT = 'json'
    VERIFY_ENDPOINT = 'https://api.nexmo.com/verify/'
    SEND_VERIFY_ENDPOINT = VERIFY_ENDPOINT + FORMAT
    CHECK_VERIFY_ENDPOINT = VERIFY_ENDPOINT + 'check/' + FORMAT

    @property
    def api_key(self):
        return self.config['SMS_KEY']

    @property
    def api_secret(self):
        return self.config['SMS_SECRET']

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
        method = method.lower()

        method = getattr(self.session, method)

        try:
            return self.parse(method(self.format_request(url, params)))
        except:
            return None

    def parse(self, response):
        return json.loads(response.text)

    def send_verify(
        self, receiver,
        message=None, sender=None, locale=None, length=None
    ):
        params = {
            'number': int(receiver),
            'brand': self.config['SMS_BRAND'],
        }

        if sender is None:
            sender = self.config['SMS_SENDER']

        if sender is not None:
            params['sender_id'] = sender

        if locale is not None:
            params['lg'] = locale

        if length is not None:
            params['code_length'] = length

        response = self.request(
            self.SEND_VERIFY_ENDPOINT,
            params
        )

        if response and response.get('request_id'):
            return response['request_id']

        return False

    def check_verify(
        self, request, code,
        ip=None
    ):
        params = {
            'request_id': request,
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
        provider = self.PROVIDER(app.config)

        provider.session = get_http_session(app)

        self.merge(provider)
