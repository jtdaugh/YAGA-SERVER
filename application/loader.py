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

from flask import Flask, request, g
from werkzeug.contrib.fixers import ProxyFix
from flask.ext.security import current_user, SQLAlchemyUserDatastore
from flanker.addresslib import set_mx_cache

from .helpers import (
    cache, db, babel, sentry, s3static, toolbar, security, redis,
    assets, s3media, celery, json_error
)
from .utils import now, DummyDict, JSONEncoder
from .admin import create_admin
from .modules.auth.models import User, Role
from .ext.redis_storage import RedisSessionInterface


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


def create_app():
    mx_cache = DummyDict()
    set_mx_cache(mx_cache)

    app = Flask(__name__)
    app.config.from_object(load_config())
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.json_encoder = JSONEncoder

    cache.init_app(app)
    db.init_app(app)
    babel.init_app(app)
    sentry.init_app(app)
    s3static.init_app(app)
    toolbar.init_app(app)
    redis.init_app(app)
    assets.init_app(app)
    s3media.init_app(app)
    celery.init_app(app)

    app.user_datastore = SQLAlchemyUserDatastore(db, User, Role)

    security.init_app(
        app,
        datastore=app.user_datastore,
        register_blueprint=False
    )

    app.session_interface = RedisSessionInterface(redis)

    create_admin(app)

    @app.before_request
    def set_locale():
        locale = request.accept_languages.best_match(app.config['LOCALES'])

        if locale is None:
            locale = app.config['BABEL_DEFAULT_LOCALE']

        g.locale = locale

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
        return g.locale

    @app.context_processor
    def locale_context():
        return {
            'locale': g.locale
        }

    @app.context_processor
    def now_context():
        return {
            'now': now()
        }

    @app.errorhandler(400)
    def error_400(e):
        return json_error(400, e)

    @app.errorhandler(401)
    def error_401(e):
        return json_error(401, e)

    @app.errorhandler(403)
    def error_403(e):
        return json_error(403, e)

    @app.errorhandler(404)
    def error_404(e):
        return json_error(404, e)

    @app.errorhandler(405)
    def error_405(e):
        return json_error(405, e)

    @app.errorhandler(500)
    def error_500(e):
        return json_error(500, e)

    from .modules.frontend.index import blueprint as index_blueprint
    from .modules.auth.api import blueprint as api_auth_blueprint

    app.register_blueprint(index_blueprint)
    app.register_blueprint(api_auth_blueprint, url_prefix='/api')

    return app, celery
