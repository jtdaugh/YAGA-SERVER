import sys
import locale


def fix_locale():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


fix_locale()


import os

from flask import Flask, request, g
from flask.json import JSONEncoder
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.utils import import_string
from speaklater import is_lazy_string
from flask.ext.script import Manager
from flask.ext.security import current_user, SQLAlchemyUserDatastore
from flanker.addresslib import set_mx_cache

from .helpers import (
    heroku, cache, db, babel, sentry, s3, toolbar, security, redis, migrate,
    json_error, now, DummyDict
)
from .admin import create_admin
from .modules.auth.models import User, Role
from .modules.frontend.index import blueprint as index_blueprint
from .modules.auth.api import blueprint as api_auth_blueprint
from .ext.redis_storage import RedisSessionInterface


def load_config():
    config = os.environ.get('ENV', 'dev')

    config = 'application.configs.{config}.Config'.format(config=config)

    config = import_string(config)

    return config


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if is_lazy_string(obj):
            obj = str(obj)
            return obj

        return JSONEncoder.default(self, obj)


def create_app():
    mx_cache = DummyDict()
    set_mx_cache(mx_cache)

    app = Flask(__name__)
    app.config.from_object(load_config())
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.json_encoder = CustomJSONEncoder

    heroku.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    babel.init_app(app)
    sentry.init_app(app)
    s3.init_app(app)
    toolbar.init_app(app)
    redis.init_app(app)
    migrate.init_app(app, db, directory='application/migrations')

    app.user_datastore = SQLAlchemyUserDatastore(db, User, Role)

    security.init_app(
        app,
        datastore=app.user_datastore,
        register_blueprint=False
    )

    app.manager = Manager(app)
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

    app.register_blueprint(index_blueprint)
    app.register_blueprint(api_auth_blueprint, url_prefix='/api')

    return app


app = create_app()
