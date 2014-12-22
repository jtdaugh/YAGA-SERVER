from __future__ import absolute_import, division, unicode_literals

from urlparse import urljoin
from functools import wraps

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
