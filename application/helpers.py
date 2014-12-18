from __future__ import absolute_import, division, unicode_literals

from collections import MutableMapping

from flask import (
    jsonify, request, render_template, make_response, abort, current_app as app
)
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babelex import Babel
from raven.contrib.flask import Sentry
from flask_s3 import FlaskS3
from flask.ext.security import Security
from flask.ext.assets import Environment
from flask_wtf.csrf import CsrfProtect
from flask.ext.babelex import lazy_gettext as _
from flask.ext.compress import Compress
from flask.ext.cors import CORS
from flask_reggie import Reggie
from flask_debugtoolbar import DebugToolbarExtension
from jinja2.exceptions import TemplateNotFound

from .ext.ssl import BaseSSLify
from .ext.redis_storage import Redis
from .ext.s3_storage import S3
from .ext.celery_storage import Celery
from .ext.geoip_storage import Geoip
from .ext.phone_storage import Phone


HTTP_STATUSES = {
    400: {
        'message': _('Bad Request'),
        'code': 'bad_request'
    },
    401: {
        'message': _('Unauthorized'),
        'code': 'unauthorized'
    },
    403: {
        'message': _('Forbidden'),
        'code': 'forbidden',
    },
    404: {
        'message': _('Not Found'),
        'code': 'not_found',
    },
    405: {
        'message': _('Method Not Allowed'),
        'code': 'method_not_allowed',
    },
    422: {
        'message': _('Unprocessable Entity'),
        'code': 'unprocessable_Entity',
    },
    429: {
        'message': _('Too Many Requests'),
        'code': 'too_many_requests',
    },
    500: {
        'message': _('Internal Server Error'),
        'code': 'internal_server_error'
    }
}


cache = Cache()
db = SQLAlchemy()
babel = Babel()
sentry = Sentry()
s3static = FlaskS3()
security = Security()
redis = Redis()
assets = Environment()
s3media = S3()
celery = Celery()
csrf = CsrfProtect()
compress = Compress()
sslify = BaseSSLify()
cors = CORS()
reggie = Reggie()
geoip = Geoip()
phone = Phone()

toolbar = DebugToolbarExtension()


class CacheDict(MutableMapping):
    def key(self, key):
        key = '{cls}:{key}'.format(
            cls=str(self.__class__),
            key=key
        )

        key = key.replace('<class', '')
        key = key.replace('>', '')
        key = key.strip()

        return key

    def __getitem__(self, key):
        return cache.get(self.key(key))

    def __setitem__(self, key, value):
        return cache.set(self.key(key), value)

    def __delitem__(self, key):
        return cache.delete(self.key(key))

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError


class MxCache(CacheDict):
    def __setitem__(self, key, value):
        value = str(value)

        super(MxCache, self).__setitem__(key, value)


class BaseResponse(object):
    def __init__(self, data=None):
        self.data = data

    @property
    def response(self):
        return {
            self.FIELD_HOLDER: self.data
        }

    def __lshift__(self, status_code):
        return self.response, status_code


class SuccessResponse(BaseResponse):
    FIELD_HOLDER = 'result'


class FailResponse(BaseResponse):
    FIELD_HOLDER = 'errors'


def error_handler(code, e):
    if request.is_xhr or request.is_json:
        response = jsonify(
            FailResponse({
                'global': [HTTP_STATUSES[code]['code']]
            }).response
        )
    else:
        try:
            response = make_response(
                render_template(
                    'errors/{code}.html'.format(
                        code=code
                    ),
                    **HTTP_STATUSES[code]
                )
            )
        except TemplateNotFound:
            response = make_response(
                render_template('errors/base.html', **HTTP_STATUSES[code])
            )

    response.status_code = code

    return response


def output_json(data, code, headers=None):
    response = jsonify(data)
    response.status_code = code

    response.data += '\n'

    if headers is not None:
        response.headers.extend(headers)

    return response


def rate_limit(scope, ident):
    prefix = 'rate_limit'

    config = app.config['RATE_LIMIT'][scope]

    ttl = int(config['INTERVAL'].total_seconds())

    if config['ENABLED']:
        key = '{prefix}:{scope}:{ident}'.format(
            prefix=prefix,
            scope=scope,
            ident=ident
        )

        amount = redis.get(key)

        if amount is not None:
            amount = int(amount)

            if amount > config['AMOUNT']:
                abort(429)

            amount = redis.incr(
                key,
                1
            )

            if amount == 1:
                redis.expire(
                    key,
                    ttl
                )
        else:
            amount = 0

            redis.setex(
                key,
                ttl,
                amount
            )
