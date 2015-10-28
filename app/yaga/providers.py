from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import json
import logging
from urllib.parse import urlencode

from apns_clerk import APNs, Message, Session
from django.utils import timezone

from app.utils import get_requests_session

from .conf import settings
from .models import Device

logger = logging.getLogger(__name__)


class NexmoResponse(
    object
):
    def __init__(self, response):
        self.response = response

        if self.response:
            if self.response.get('error_text'):
                if self.response.get('status') not in ('16', '17'):
                    _logger = logger.error
                else:
                    _logger = logger.warning
            else:
                _logger = logger.info

            _logger(response)

    def is_valid(self):
        if self.response and self.response.get('status') == '0':
            return True

        return False

    def exceeded(self):
        if self.response and self.response.get('status') == '17':
            return True

        return False

    @property
    def request_id(self):
        if self.response and self.response.get('request_id'):
            return self.response['request_id']

        return False


class NexmoProvider(
    object
):
    FORMAT = 'json'

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
        except Exception as e:
            logger.exception(e)

            data = None

        return NexmoResponse(data)

    def parse(self, response):
        return json.loads(response.text)


class NexmoCodeProvider(
    NexmoProvider
):
    VERIFY_ENDPOINT = 'https://api.nexmo.com/verify/'
    SEND_VERIFY_ENDPOINT = '{verify_endpoint}{format}'.format(
        verify_endpoint=VERIFY_ENDPOINT,
        format=FORMAT
    )
    CHECK_VERIFY_ENDPOINT = '{verify_endpoint}check/{format}'.format(
        verify_endpoint=VERIFY_ENDPOINT,
        format=FORMAT
    )
    
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
        else:
            params['lg'] = settings.YAGA_SMS_DEFAULT_LANGUAGE_CODE

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


class NexmoNotificationProvider(
    NexmoProvider
): 
    ALERT_ENDPOINT = 'https://rest.nexmo.com/sc/us/alert/'
    SEND_NOTIFICATION_ENDPOINT = '{verify_endpoint}{format}'.format(
        verify_endpoint=ALERT_ENDPOINT,
        format=FORMAT
    )
    CHECK_BLACKLIST_ENDPOINT = '{verify_endpoint}check/{format}'.format(
        verify_endpoint=ALERT_ENDPOINT,
        format=FORMAT
    )

    def sendInvite(
        self, receiver,
        sender=None
    ):
        params = {
            'template': 0,
            'to': int(receiver),
            'username': sender.name,
            'link': settings.YAGA_SMS_INVITE_SUFFIX,
        }

        return self.request(
            self.SEND_NOTIFICATION_ENDPOINT,
            params
        )

    def sendVideo(
        self, receiver,
        sender=None, group=None, video=None
    ):
        link = '{base_url}{video_id}'.format(
            base_url=settings.YAGA_SMS_VIDEO_BASE_URL,
            video_id=str(video.id)[:7]
        )

        params = {
            'template': 1,
            'to': int(receiver),
            'username': sender.name,
            'link': link
        }

        if group is not None:
            params['template'] = 2
            params['group'] = group.name

        return self.request(
            self.SEND_NOTIFICATION_ENDPOINT,
            params
        )


class APNSProvider(
    object
):
    _task = None

    def __init__(self):
        self.release_service()

    def load_service(self):
        session = Session()

        connection = session.get_connection(
            settings.YAGA_APNS_MODE,
            cert_file=settings.YAGA_APNS_CERT
        )

        service = APNs(connection)

        return service

    def release_service(self):
        if hasattr(self, 'service'):
            del self.service

        self.service = None
        self.created_at = None

    def setup_service(self):
        self.service = self.load_service()
        self.created_at = timezone.now()

    def get_service(self):
        if not settings.YAGA_APNS_POOL:
            return self.load_service()

        elif self.service is None:
            self.setup_service()
        elif (
            timezone.now() - self.created_at
            >
            settings.YAGA_APNS_POOL_TIMEOUT
        ):
            self.release_service()
            self.setup_service()

        return self.service

    @property
    def task(self):
        if self._task is None:
            from .tasks import APNSPushTask

            self._task = APNSPushTask

        return self._task

    def schedule(self, receivers, **kwargs):
        if receivers:
            self.task().delay(receivers, **kwargs)

    def push(self, receivers, **kwargs):
        service = self.get_service()

        if not isinstance(receivers, (list, tuple)):
            receivers = (receivers,)

        message = Message(
            receivers,
            **kwargs
        )

        response = service.send(message)

        for token, (reason, explanation) in list(response.failed.items()):
            try:
                device = Device.objects.get(
                    token=token
                )

                device.delete()
            except Device.DoesNotExist:
                pass

            if token in receivers:
                receivers.remove(token)

        if response.needs_retry():
            self.schedule(
                receivers,
                **kwargs
            )

    def feedback(self):
        session = Session()

        connection = session.get_connection(
            settings.YAGA_APNS_FEEDBACK_MODE,
            cert_file=settings.YAGA_APNS_CERT
        )

        service = APNs(connection)

        for token, when in service.feedback():
            device = Device.objects.filter(
                token=token,
                vendor=Device.vendor_choices.IOS
            ).first()

            if device:
                if (
                    device.updated_at.astimezone(
                        timezone.utc
                    ).replace(tzinfo=None) < when
                ):
                    device.delete()

        del service


apns_provider = APNSProvider()

code_provider = NexmoCodeProvider()

sms_notification_provider = NexmoNotificationProvider()
