from __future__ import absolute_import, division, unicode_literals

from urlparse import urljoin
from functools import wraps

import ujson
import regex
import requests
from django.conf import settings
from django.conf.urls import url
from django.utils.http import urlquote
from django.views.decorators.cache import cache_page
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.functional import SimpleLazyObject
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import Site
from django.utils import six
from rest_framework.parsers import BaseParser
from rest_framework.exceptions import ParseError
from rest_framework.renderers import BaseRenderer
from rest_framework.settings import api_settings
from raven.contrib.django import DjangoClient

from app import celery
from requestprovider import get_request


rurl_re = regex.compile('<((\w+:)?\w+)>')


def regex_substituter(match):
    rule = match.groups()[0]
    name, pattern = rule.split(':')
    return '(?P<%s>%s)' % (name, settings.URL_REGEX_REPLACES[pattern])


def translate_regex(pattern):
    return rurl_re.sub(regex_substituter, pattern)[1:]


def rurl(pattern, *args, **kwargs):
    return url(translate_regex(pattern), *args, **kwargs)


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


def create_requests_session():
    session = requests.Session()

    adapter = requests.adapters.HTTPAdapter(
        max_retries=settings.HTTP_RETRIES
    )

    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session


class UJSONRenderer(BaseRenderer):
    media_type = 'application/json'
    format = 'json'
    ensure_ascii = not api_settings.UNICODE_JSON
    charset = None

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return bytes()

        renderer_context = renderer_context or {}

        ret = ujson.dumps(
            data,
            ensure_ascii=self.ensure_ascii
        )

        return ret


class UJSONParser(BaseParser):
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


class SentryClient(DjangoClient):
    def get_user_info(self, user):
        if not user.is_authenticated():
            return {'is_authenticated': False}

        user_info = {
            'id': user.pk.hex,
            'is_authenticated': True,
        }

        user_info['username'] = user.get_username()

        return user_info

    def send_integrated(self, kwargs):
        print kwargs
        print send_raw_integrated.delay(kwargs)

    def send_encoded(self, *args, **kwargs):
        print args, kwargs
        print send_raw.delay(*args, **kwargs)


@celery.task
def send_raw_integrated(kwargs):
    from raven.contrib.django.models import get_client
    super(SentryClient, get_client()).send_integrated(kwargs)


@celery.task
def send_raw(*args, **kwargs):
    from raven.contrib.django.models import get_client
    super(SentryClient, get_client()).send_encoded(*args, **kwargs)
