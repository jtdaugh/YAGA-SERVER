from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import json
import logging
from urllib.parse import urlencode

from apnsclient import APNs, Message, Session
from django.utils import timezone
from django.utils.lru_cache import lru_cache
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import override

from app.utils import get_requests_session

from .conf import settings
from .models import Contact, Device, Member, Post

logger = logging.getLogger(__name__)


class NexmoResponse(
    object
):
    def __init__(self, response):
        self.response = response

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
    VERIFY_ENDPOINT = 'https://api.nexmo.com/verify/'
    SEND_VERIFY_ENDPOINT = '{verify_endpoint}{format}'.format(
        verify_endpoint=VERIFY_ENDPOINT,
        format=FORMAT
    )
    CHECK_VERIFY_ENDPOINT = '{verify_endpoint}check/{format}'.format(
        verify_endpoint=VERIFY_ENDPOINT,
        format=FORMAT
    )

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
        self.release_service()

    def load_service(self):
        session = Session()

        connection = session.get_connection(
            settings.YAGA_APNS_MODE, cert_file=settings.YAGA_APNS_CERT
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

    def scheduled_task(self, *args, **kwargs):
        APNSPush().delay(*args, **kwargs)

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
            Device.objects.filter(
                token=token
            ).delete()

            if token in receivers:
                receivers.remove(token)

        if response.needs_retry():
            self.scheduled_task(
                receivers,
                **kwargs
            )

        return response


class IOSNotification(
    object
):
    VENDOR = Device.IOS
    BROADCAST = False
    TARGET = False

    def __init__(self, **kwargs):
        for key, value in list(kwargs.items()):
            setattr(self, key, value)

        self.push()

    def rate_limited(self):
        return False

    def get_broadcast_message(self):
        raise NotImplementedError

    def get_broadcast_kwargs(self):
        raise NotImplementedError

    def get_target_message(self):
        raise NotImplementedError

    def get_target_kwargs(self):
        raise NotImplementedError

    def get_group(self):
        raise NotImplementedError

    def get_target(self):
        raise NotImplementedError

    def get_emitter(self):
        raise NotImplementedError

    def get_broadcast_exclude(self):
        return {
            'user': self.get_emitter()
        }

    def get_broadcast_receivers(self):
        return [member.user for member in self.get_group().member_set.filter(
            mute=False
        ).exclude(
            **self.get_broadcast_exclude()
        )]

    def get_target_receivers(self):
        return [self.get_target()]

    def get_devices(self, users):
        devices = Device.objects.filter(
            vendor=self.VENDOR,
            user__in=users
        )

        return devices

    def get_token_map(self, devices):
        token_map = {}

        for device in devices:
            if token_map.get(device.locale) is None:
                token_map[device.locale] = []

            token_map[device.locale].append(device.token)

        return token_map

    def push_broadcast(self):
        devices = self.get_devices(self.get_broadcast_receivers())

        token_map = self.get_token_map(devices)

        if token_map:
            for locale, tokens in list(token_map.items()):
                with override(locale):
                    apns_provider.scheduled_task(
                        tokens,
                        alert=self.get_broadcast_message().format(
                            **self.get_broadcast_kwargs()
                        )
                    )

    def push_target(self):
        devices = self.get_devices(self.get_target_receivers())

        token_map = self.get_token_map(devices)

        if token_map:
            for locale, tokens in list(token_map.items()):
                with override(locale):
                    apns_provider.scheduled_task(
                        tokens,
                        alert=self.get_target_message().format(
                            **self.get_target_kwargs()
                        )
                    )

    def push(self):
        if not self.rate_limited():
            if self.TARGET:
                self.push_target()

            if self.BROADCAST:
                self.push_broadcast()


class NewVideoIOSNotification(
    IOSNotification
):
    BROADCAST = True

    def rate_limited(self):
        previous_post = Post.objects.filter(
            user=self.get_emitter(),
            group=self.get_group(),
            ready=True
        ).exclude(
            pk=self.post.pk
        ).order_by(
            '-ready_at'
        ).first()

        if previous_post is not None:
            return not (
                self.post.ready_at - settings.YAGA_PUSH_POST_WINDOW
                >
                previous_post.ready_at
            )
        else:
            return False

    def get_group(self):
        return self.post.group

    def get_emitter(self):
        return self.post.user

    def get_broadcast_message(self):
        return _('{user} posted into {group}')

    def get_broadcast_kwargs(self):
        return {
            'group': self.get_group().name,
            'user': self.get_emitter()
        }


class NewMemberIOSNotification(
    IOSNotification
):
    BROADCAST = True
    TARGET = True

    def get_group(self):
        return self.member.group

    def get_emitter(self):
        return self.member.creator

    def get_target(self):
        return self.member.user

    def get_broadcast_exclude(self):
        return {
            'user__in': [self.get_emitter(), self.get_target()]
        }

    def get_broadcast_message(self):
        return _('{creator} added {member} to {group}')

    def get_broadcast_kwargs(self):
        return {
            'group': self.member.group.name,
            'member': self.member.user.get_username(),
            'creator': self.member.creator.get_username()
        }

    def get_target_message(self):
        return _('{creator} has added you to {group}')

    def get_target_kwargs(self):
        return self.get_broadcast_kwargs()


class NewLikeIOSNotification(
    IOSNotification
):
    TARGET = True

    def get_target(self):
        return self.like.post.user

    def get_target_message(self):
        return _('{user} liked your video in {group}')

    def get_target_kwargs(self):
        return {
            'user': self.like.user.get_username(),
            'group': self.like.post.group.name,
        }


class DeleteMemberIOSNotification(
    IOSNotification
):
    BROADCAST = True
    TARGET = True

    def get_group(self):
        return self.member.group

    def get_emitter(self):
        return self.deleter

    def get_target(self):
        return self.member.user

    def get_broadcast_message(self):
        return _('{deleter} removed {member} from {group}')

    def get_broadcast_kwargs(self):
        return {
            'group': self.member.group.name,
            'member': self.member.user.get_username(),
            'deleter': self.deleter
        }

    def get_target_message(self):
        return _('{deleter} has removed you from {group}')

    def get_target_kwargs(self):
        return self.get_broadcast_kwargs()


class GroupLeaveIOSNotification(
    IOSNotification
):
    BROADCAST = True

    def get_group(self):
        return self.member.group

    def get_emitter(self):
        return self.member.user

    def get_broadcast_message(self):
        return _('{member} has left {group}')

    def get_broadcast_kwargs(self):
        return {
            'group': self.member.group.name,
            'member': self.member.user.get_username(),
        }


class NewUserIOSNotification(
    IOSNotification
):
    @lru_cache()
    def get_groups(self):
        return [member.group for member in Member.objects.filter(
            user=self.user
        )]

    def get_emitter(self):
        return self.user

    def push(self):
        self.push_broadcast_groups()

        self.push_broadcast_contacts()

    def push_broadcast_groups(self):
        groups = self.get_groups()

        self.get_broadcast_message = lambda: _('{member} joined {group}')

        for group in groups:
            self.get_broadcast_kwargs = lambda: {
                'member': self.user.get_username(),
                'group': group.name
            }

            self.get_group = lambda: group

            self.push_broadcast()

    def push_broadcast_contacts(self):
        users = [member.user for member in Member.objects.filter(
            group__in=self.get_groups()
        ).distinct('user')]

        self.get_broadcast_receivers = lambda: [
            contact.user for contact in Contact.objects.filter(
                phones__contains=[self.user.phone.as_e164],
            ).exclude(
                user__in=users
            )
        ]

        self.get_broadcast_message = lambda: _('{member} joined Yaga')

        self.get_broadcast_kwargs = lambda: {
            'member': self.user.get_username()
        }

        self.push_broadcast()


apns_provider = APNSProvider()

code_provider = NexmoProvider()

from .tasks import APNSPush  # noqa # isort:skip
