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
from flask.ext.compress import Compress
from flask.ext.cors import CORS
from flask_reggie import Reggie
from flask_debugtoolbar import DebugToolbarExtension
from jinja2.exceptions import TemplateNotFound
from flask.ext.babelex import lazy_gettext as _

from .ext.ssl import BaseSSLify
from .ext.redis_storage import Redis
from .ext.s3_storage import S3
from .ext.celery_storage import Celery
from .ext.geoip_storage import Geoip
from .ext.phone_storage import Phone


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

    def __iter__(self):
        for key, value in self.response.items():
            yield key, value


class SuccessResponse(BaseResponse):
    FIELD_HOLDER = 'result'


class FailResponse(BaseResponse):
    FIELD_HOLDER = 'errors'


class HttpStatus(int):
    def __new__(cls, *args, **kwargs):
        return super(HttpStatus, cls).__new__(cls, kwargs.pop('status'))

    def __init__(self, *args, **kwargs):
        self.message = kwargs['message']
        self.json_message = kwargs['json_message']


class Http(object):
    HTTP_STATUSES = {
        'OK': {
            'message': _('OK'),
            'json_message': 'ok',
            'status': 200
        },
        'CREATED': {
            'message': _('Created'),
            'json_message': 'created',
            'status': 201
        },
        'NO_CONTENT': {
            'message': _('No Content'),
            'json_message': 'no_content',
            'status': 204
        },
        'MOVED_PERMANENTLY': {
            'message': _('Moved Permanently'),
            'json_message': 'moved_permanently',
            'status': 301
        },
        'FOUND': {
            'message': _('Found'),
            'json_message': 'found',
            'status': 302
        },
        'BAD_REQUEST': {
            'message': _('Bad Request'),
            'json_message': 'bad_request',
            'status': 400
        },
        'UNAUTHORIZED': {
            'message': _('Unauthorized'),
            'json_message': 'unauthorized',
            'status': 401
        },
        'FORBIDDEN': {
            'message': _('Forbidden'),
            'json_message': 'forbidden',
            'status': 403
        },
        'NOT_FOUND': {
            'message': _('Not Found'),
            'json_message': 'not_found',
            'status': 404
        },
        'METHOD_NOT_ALLOWED': {
            'message': _('Method Not Allowed'),
            'json_message': 'method_not_allowed',
            'status': 405
        },
        'PRECONDITION_FAILED': {
            'message': _('Precondition Failed'),
            'json_message': 'precondition_failed',
            'status': 412
        },
        'UNPROCESSABLE_ENTITY': {
            'message': _('Unprocessable Entity'),
            'json_message': 'unprocessable_entity',
            'status': 422
        },
        'TOO_MANY_REQUESTS': {
            'message': _('Too Many Requests'),
            'json_message': 'too_many_requests',
            'status': 429
        },
        'INTERNAL_SERVER_ERROR': {
            'message': _('Internal Server Error'),
            'json_message': 'internal_server_error',
            'status': 500
        }
    }

    def __init__(self):
        for ident, options in self.HTTP_STATUSES.items():
            status = HttpStatus(**options)

            setattr(self, ident, status)

    def __iter__(self):
        for obj in self.__dict__.values():
            if isinstance(obj, HttpStatus):
                yield obj


def error_handler(status, e):
    if request.is_xhr or request.is_json:
        response = jsonify(
            FailResponse({
                'global': [status.json_message]
            }).response
        )
    else:
        context = {
            'status': status,
            'message': status.message
        }

        try:
            response = make_response(
                render_template(
                    'errors/{status}.html'.format(
                        status=status
                    ),
                    **context
                )
            )
        except TemplateNotFound:
            response = make_response(
                render_template(
                    'errors/base.html',
                    **context
                )
            )

    response.status_code = status

    return response


def output_json(data, status, headers=None):
    response = jsonify(data)
    response.status_code = status

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


http = Http()
