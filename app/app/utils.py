from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from functools import wraps
from urllib.parse import urljoin

import regex
import requests
import ujson
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch, reverse
from django.utils import six
from django.utils.functional import SimpleLazyObject
from django.utils.http import urlquote
from django.views.decorators.cache import cache_page
from raven.contrib.django import DjangoClient
from rest_framework.exceptions import ParseError
from rest_framework.parsers import BaseParser
from rest_framework.renderers import BaseRenderer
from rest_framework.settings import api_settings

from requestprovider import get_request

from . import celery

try:
    from django.utils.encoding import (  # noqa
        smart_text, force_text,
        smart_bytes, force_bytes
    )
except ImportError:
    from django.utils.encoding import (  # noqa
        smart_unicode as smart_text, force_unicode as force_text,
        smart_bytes, force_bytes
    )


def u(value):
    if isinstance(value, six.binary_type):
        value = value.decode()

    return value


def b(value):
    if isinstance(value, six.string_types):
        value = value.encode()

    return value


def nless(content):
    content = regex.sub('\n{2,}', '\n', content)
    content = regex.sub('\n', ' ', content)
    return content


def sless(content):
    content = regex.sub(r'\s{2,}', ' ', content)
    content = regex.sub(r'>\s', '>', content)
    content = regex.sub(r'\s<', '<', content)
    content = regex.sub(r'\="\s', '="', content)
    content = regex.sub(r'\s"', '"', content)
    content = content.strip(' ')
    return content


def snless(content):
    return sless(nless(content))


def show_toolbar(request):
    return settings.DEBUG_TOOLBAR


def user_cache_view(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if settings.VIEW_CACHE:
            request = args[0]

            if not request.user.is_authenticated():
                _fn = cache_page(settings.VIEW_CACHE_TIMEOUT)(fn)
            else:
                _fn = fn
        else:
            _fn = fn

        return _fn(*args, **kwargs)
    return wrapper


def cache_view(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if settings.VIEW_CACHE:
            _fn = cache_page(settings.VIEW_CACHE_TIMEOUT)(fn)
        else:
            _fn = fn

        return _fn(*args, **kwargs)
    return wrapper


def reverse_host(pattern, args=None, kwargs=None):
    if args is None:
        args = []

    if kwargs is None:
        kwargs = {}

    try:
        url = reverse(pattern, args=args, kwargs=kwargs)
    except NoReverseMatch:
        url = urlquote(pattern)

    try:
        request = get_request()

        url = request.build_absolute_uri(url)
    except ImproperlyConfigured:
        site = Site.objects.get_current()

        if site.domain.startswith('http'):
            domain = site.domain
        else:
            if settings.HTTPS:
                schema = 'https://'
            else:
                schema = 'http://'

            domain = '%s%s' % (schema, site.domain)

        url = urljoin(domain, url)

    return url


def reverse_host_lazy(pattern, args=None, kwargs=None):
    def _reverse_host_lazy():
        return reverse_host(pattern, args=args, kwargs=kwargs)

    return SimpleLazyObject(_reverse_host_lazy)


def _get_requests_session():
    session = requests.Session()

    adapter = requests.adapters.HTTPAdapter(
        max_retries=settings.HTTP_RETRIES
    )

    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session


_requests_session = None


def get_requests_session(cached=True):
    if cached:
        global _requests_session

        if _requests_session is None:
            _requests_session = _get_requests_session()

        return _requests_session
    else:
        return _get_requests_session()


def get_sentry_client():
    def _get_sentry_cleint():
        from raven.contrib.django.models import get_client
        return get_client()

    return SimpleLazyObject(_get_sentry_cleint)


class UJSONRenderer(
    BaseRenderer
):
    media_type = 'application/json'
    format = 'json'
    ensure_ascii = not api_settings.UNICODE_JSON
    charset = None

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return bytes()

        renderer_context = renderer_context or {}

        return ujson.dumps(
            data,
            ensure_ascii=self.ensure_ascii
        )


class UJSONParser(
    BaseParser
):
    media_type = 'application/json'
    renderer_class = UJSONRenderer

    def parse(self, stream, media_type=None, parser_context=None):
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)

        try:
            data = stream.read().decode(encoding)

            return ujson.loads(data)
        except Exception as exc:
            raise ParseError('JSON parse error - %s' % six.text_type(exc))


class SentryCeleryClient(
    DjangoClient
):
    def get_user_info(self, user):
        if not user.is_authenticated():
            user_info = {'is_authenticated': False}
        else:
            user_info = {
                'id': smart_text(user.pk),
                'is_authenticated': True,
                'username': user.get_username()
            }

        return user_info

    def send_integrated(self, kwargs):
        return SendRawIntegrated().delay(kwargs)

    def send_encoded(self, *args, **kwargs):
        return SendRaw().delay(*args, **kwargs)


class SendRawIntegrated(
    celery.Task
):
    def run(self, kwargs):
        super(SentryCeleryClient, sentry_client).send_integrated(kwargs)


class SendRaw(
    celery.Task
):
    def run(self, *args, **kwargs):
        super(SentryCeleryClient, sentry_client).send_encoded(*args, **kwargs)


sentry_client = get_sentry_client()
