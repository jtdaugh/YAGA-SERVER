from __future__ import absolute_import, division, unicode_literals

from flask import jsonify
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babelex import Babel
from raven.contrib.flask import Sentry
from flask_s3 import FlaskS3
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.security import Security
from flask.ext.migrate import Migrate
from flask.ext.assets import Environment
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


def json_error(code, e):
    message = HTTP_STATUS_CODES.get(code)

    if not message:
        try:
            message = str(e)
        except:
            pass

    data = {
        'result': 'fail'
    }

    if message:
        data['message'] = message

    response = jsonify(data)
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
migrate = Migrate()
assets = Environment()
s3media = S3()
celery = Celery()
