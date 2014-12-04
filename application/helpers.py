from __future__ import absolute_import, division, unicode_literals

from collections import MutableMapping

from flask import jsonify, request, render_template, make_response
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babelex import Babel
from raven.contrib.flask import Sentry
from flask_s3 import FlaskS3
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.security import Security
from flask.ext.assets import Environment
from flask_wtf.csrf import CsrfProtect
from flask.ext.babelex import lazy_gettext as _

from .ext.redis_storage import Redis
from .ext.s3_storage import S3
from .ext.celery_storage import Celery


HTTP_STATUS_CODES = {
    400: _('Bad Request'),
    401: _('Unauthorized'),
    403: _('Forbidden'),
    404: _('Not Found'),
    405: _('Method Not Allowed'),
    500: _('Internal Server Error'),
}


def error_handler(code, e):
    message = HTTP_STATUS_CODES[code]

    if request.is_xhr or request.is_json:
        data = {
            'error': message
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

    if headers is not None:
        response.headers.extend(headers)

    return response


cache = Cache()
db = SQLAlchemy()
babel = Babel()
sentry = Sentry()
s3static = FlaskS3()
toolbar = DebugToolbarExtension()
security = Security()
redis = Redis()
assets = Environment()
s3media = S3()
celery = Celery()
csrf = CsrfProtect()


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
