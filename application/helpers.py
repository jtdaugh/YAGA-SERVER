import datetime

from flask import jsonify
from flask.ext.cache import Cache
from flask.ext.mongoengine import MongoEngine
from flask.ext.babelex import Babel
from raven.contrib.flask import Sentry
from flask_s3 import FlaskS3
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.security import Security
from flask.ext.babelex import lazy_gettext as _

from .decorators import marshal_with_form, anonymous_user_required, login_required  # noqa


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


def now():
    return datetime.datetime.utcnow()


cache = Cache()
db = MongoEngine()
babel = Babel()
sentry = Sentry()
s3 = FlaskS3()
toolbar = DebugToolbarExtension()
security = Security()


from .mixins import Api, Resource, Form, Validator, BaseAdminView # noqa
