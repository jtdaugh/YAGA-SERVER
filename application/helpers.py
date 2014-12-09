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
from flask.ext.security import Security, AnonymousUser
from flask.ext.assets import Environment
from flask_wtf.csrf import CsrfProtect
from flask.ext.babelex import lazy_gettext as _
from flask.ext.compress import Compress
from flask.ext.cors import CORS
from flask_reggie import Reggie
from flask_debugtoolbar import DebugToolbarExtension

from .ext.ssl import BaseSSLify
from .ext.redis_storage import Redis
from .ext.s3_storage import S3
from .ext.celery_storage import Celery
from .ext.geoip_storage import Geoip
from .utils import now


HTTP_STATUS_CODES = {
    400: _('Bad Request'),
    401: _('Unauthorized'),
    403: _('Forbidden'),
    404: _('Not Found'),
    405: _('Method Not Allowed'),
    429: _('Too Many Requests'),
    500: _('Internal Server Error')
}


def error_handler(code, e):
    message = HTTP_STATUS_CODES[code]

    if request.is_xhr or request.is_json:
        data = {
            'errors': {
                'global': message
            }
        }

        response = jsonify(data)
    else:
        response = make_response(
            render_template('error.html', code=code, message=message)
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

    if config['ENABLED']:
        key = '{prefix}:{scope}:{ident}'.format(
            prefix=prefix,
            scope=scope,
            ident=ident
        )

        requests = cache.get(key)

        if requests is not None:
            requests['amount'] += 1

            if requests['amount'] > config['REQUESTS']:
                abort(429)

            ttl = int((requests['ttl'] - now()).total_seconds())

            if ttl > 0:
                cache.set(
                    key,
                    requests,
                    ttl
                )
        else:
            requests = {
                'amount': 1,
                'ttl': now() + config['INTERVAL']
            }

            ttl = int(config['INTERVAL'].total_seconds())

            cache.set(
                key,
                requests,
                ttl
            )


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
    STATUSES = {
        'success': 'success',
        'fail': 'fail'
    }
    DEFAULT_RESULT = {}
    DEFAULT_ERRORS = []

    def __init__(self, data=None):
        self.status = self.DEFAULT_STATUS

        self.result = self.DEFAULT_RESULT

        self.errors = self.DEFAULT_ERRORS

        if data is not None:
            setattr(self, self.FIELD_HOLDER, data)

    @property
    def response(self):
        return {
            'status': self.STATUSES[self.status],
            'result': self.result,
            'errors': self.errors
        }

    def __lshift__(self, status_code):
        return self.response, status_code


class SuccessResponse(BaseResponse):
    DEFAULT_STATUS = 'success'

    FIELD_HOLDER = 'result'


class FailResponse(BaseResponse):
    DEFAULT_STATUS = 'fail'

    FIELD_HOLDER = 'errors'


class BaseAnonymousUser(AnonymousUser):
    def __init__(self, *args, **kwargs):
        super(BaseAnonymousUser, self).__init__(*args, **kwargs)
