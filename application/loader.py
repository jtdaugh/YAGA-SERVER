from __future__ import absolute_import, division, unicode_literals

from future import standard_library
standard_library.install_aliases()

import sys
import locale


reload(sys)
sys.setdefaultencoding('utf-8')

try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except ValueError:
    locale.setlocale(locale.LC_ALL, ('en_US', 'UTF-8'))


from os import environ
from functools import partial

from flask import Flask, request, g
from werkzeug.contrib.fixers import ProxyFix
from flask.ext.security import current_user, SQLAlchemyUserDatastore
from flanker.addresslib import set_mx_cache
from flask_debugtoolbar.panels import sqlalchemy as sqlalchemy_toolbar

from .helpers import (
    cache, db, babel, sentry, s3static, toolbar, security, redis,
    assets, s3media, csrf, celery, compress, sslify, cors, reggie,
    geoip, error_handler, HTTP_STATUS_CODES, MxCache
)
from .utils import now, BaseJSONEncoder, dummy_callback, detect_json
from .admin import create_admin
from .modules.auth.models import User, Role
from .modules.auth.repository import token_storage
from .ext.redis_storage import RedisSessionInterface
from .modules.auth.sessions import SqlSessionInterface
from .decorators import session_marker, header_marker


class Application(Flask):
    pass


def get_environment():
    if environ.get('DYNO'):
        config = 'heroku'
    elif environ.get('TESTING'):
        config = 'test'
    else:
        config = 'local'

    return config


def load_config():
    environment = get_environment()

    if environment == 'heroku':
        from .configs.heroku import Config
    elif environment == 'test':
        from .configs.test import Config
    elif environment == 'local':
        from .configs.local import Config
    else:
        raise ImportError

    return Config


def setup_mx_cache():
    mx_cache = MxCache()
    set_mx_cache(mx_cache)


def setup_sentry():
    sentry.add_sentry_id_header = dummy_callback


def setup_toolbar(csrf):
    sqlalchemy_toolbar.sql_select = csrf.exempt(
        sqlalchemy_toolbar.sql_select
    )


def create_app():
    setup_mx_cache()
    setup_sentry()
    app = Application(__name__)
    app.config.from_object(load_config())
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.json_encoder = BaseJSONEncoder

    cache.init_app(app)
    db.init_app(app)
    babel.init_app(app)
    sentry.init_app(app)
    s3static.init_app(app)
    redis.init_app(app)
    assets.init_app(app)
    s3media.init_app(app)
    csrf.init_app(app)
    celery.init_app(app)
    compress.init_app(app)
    sslify.init_app(app)
    cors.init_app(app, resources=r'/api/*', headers='Content-Type')
    reggie.init_app(app)
    geoip.init_app(app)

    setup_toolbar(csrf)
    toolbar.init_app(app)

    create_admin(app)

    app.user_datastore = SQLAlchemyUserDatastore(db, User, Role)

    security.init_app(
        app,
        datastore=app.user_datastore,
        register_blueprint=False
    )

    app.login_manager.session_protection = None

    if app.config['SESSION_ENGINE'] == 'redis':
        app.session_interface = RedisSessionInterface(redis)
    elif app.config['SESSION_ENGINE'] == 'sql':
        app.session_interface = SqlSessionInterface()

    app.login_manager.user_loader(
        session_marker(app.login_manager.user_callback)
    )

    app.login_manager.header_loader(
        header_marker(token_storage.user_header_loader)
    )

    @app.login_manager.token_loader
    def load_user_from_token(value):
        return None

    @app.before_request
    def set_locale():
        locale = request.accept_languages.best_match(app.config['LOCALES'])

        if locale is None:
            locale = app.config['BABEL_DEFAULT_LOCALE']

        g.locale = locale

    @app.before_request
    def is_json():
        request.is_json = detect_json()

    @app.before_request
    def set_user():
        g.user = current_user

    @app.after_request
    def after_request_callbacks(response):
        for callback in g.get('after_request_callbacks', []):
            callback(response)

        return response

    @babel.localeselector
    def get_locale():
        if g.get('locale'):
            return g.locale

        return app.config['BABEL_DEFAULT_LOCALE']

    @app.context_processor
    def now_context():
        return {
            'now': now()
        }

    for code in HTTP_STATUS_CODES:
        app.errorhandler(code)(partial(error_handler, code))

    @csrf.error_handler
    def csrf_error(e):
        return error_handler(400, e)

    from .modules.frontend.views.index import blueprint as index
    from .modules.auth.api.v1 import blueprint as api_auth_v1
    from .modules.auth.views import blueprint as auth
    from .modules.environment.api.v1 import blueprint as api_environment_v1

    app.register_blueprint(index)
    app.register_blueprint(auth)
    app.register_blueprint(api_auth_v1, url_prefix='/api/v1')
    app.register_blueprint(api_environment_v1, url_prefix='/api/v1')

    from . import modules

    celery.autodiscover(modules)

    return app, celery
