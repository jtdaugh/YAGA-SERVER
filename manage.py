#!/usr/bin/env python
from __future__ import (
    absolute_import, division, unicode_literals, print_function
)
from application.loader import create_app

import os
from subprocess import Popen
from urllib.parse import unquote

import flask_s3
from IPython import embed
from babel import support
from flask import json, g
from flask.ext.script import Command
from flask.ext.migrate import Migrate
from flask.ext.script import Manager
from flask.ext.migrate import MigrateCommand
from flask.ext.assets import ManageAssets
from flask.ext.testing.utils import _make_test_response
from flask.ext.babelex import lazy_gettext as lazy_gettext, gettext
from sqlalchemy_utils.functions import create_database, database_exists

from application.tests.utils import create_json_client
from application.helpers import assets, cache, db, redis, s3media, geoip
from application.modules.auth.commands import CreateSuperUser, SyncRoles
from application.modules.auth.models import User, Role, Session, Token
from application.modules.auth.repository import (
    user_storage, role_storage, session_storage, token_storage
)


app, celery = create_app()

manager = Manager(app)
migrate = Migrate(app, db, directory='application/migrations')


class ShellMixin(object):
    def local(self, cmd):
        shell = Popen(
            cmd,
            shell=True
        )
        shell.wait()


class Shell(Command):
    def run(self):
        app.config['TESTING'] = True

        app.response_class = _make_test_response(app.response_class)

        client = app.test_client()

        ctx = app.test_request_context()
        ctx.push()

        json_client = create_json_client(app, client)

        embed(user_ns={
            'ctx': ctx,

            'client': client,
            'json_client': json_client,

            'g': g,

            'app': app,
            'celery': celery,

            'cache': cache,
            'db': db,
            'redis': redis,
            's3media': s3media,
            'geoip': geoip,

            'User': User,
            'Role': Role,
            'Session': Session,
            'Token': Token,

            'user_storage': user_storage,
            'role_storage': role_storage,
            'session_storage': session_storage,
            'token_storage': token_storage,

            'json': json,
            'lazy_gettext': lazy_gettext,
            'gettext': gettext,
        })

        ctx.pop()


class Debug(Command):
    def run(self):
        app.run(
            host=app.config['APP_HOST'],
            port=app.config['APP_PORT'],
            debug=True,
            use_debugger=True,
            use_reloader=True
        )


class CreateAll(Command):
    def run(self):
        db.create_all()


class UrlMap(Command):
    def run(self):
        output = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            line = unquote(
                '{:50s} {:20s} {}'.format(rule.endpoint, methods, rule)
            )
            output.append(line)

        output.sort()

        for line in output:
            print(line)


class Collectstatic(Command):
    def run(self):
        flask_s3.create_all(app)


class MakeMessages(Command, ShellMixin):
    def run(self):
        self.local('pybabel extract --no-location -F babel.cfg -o messages.pot .')

        for locale in app.config['LOCALES']:
            if not os.path.exists('application/translations/{locale}/LC_MESSAGES/messages.po'.format(locale=locale)):
                self.local('pybabel init -i  messages.pot -d application/translations -l {locale}'.format(locale=locale))

            self.local('pybabel update -i messages.pot -d application/translations -l {locale}'.format(locale=locale))

        os.unlink('messages.pot')


class CompileMessages(Command, ShellMixin):
    def gettext_json(self, path, locale, domain):
        translations = support.Translations.load(
            path, locale, domain=domain
        )

        keys = translations._catalog.keys()
        keys.sort()
        ret = {}

        for k in keys:
            v = translations._catalog[k]
            if isinstance(k, tuple):
                if k[0] not in ret:
                    ret[k[0]] = []
                ret[k[0]].append(v)
            else:
                ret[k] = v

        try:
            del ret['']
        except:
            pass

        return json.dumps(ret, ensure_ascii=False, indent=True)

    def run(self):
        self.local('pybabel compile -f -d application/translations')

        domain = 'messages'
        path = 'application/translations'

        for locale in app.config['LOCALES']:
            filename = 'application/static/translations/{locale}.json'.format(locale=locale)

            result = self.gettext_json(path, locale, domain)

            with open(filename, 'w+') as f:
                f.write(result.encode('utf8'))


class ClearCache(Command):
    def run(self):
        cache.clear()


class EnsureDb(Command):
    def run(self):
        if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
            create_database(app.config['SQLALCHEMY_DATABASE_URI'])


manager.add_command('shell', Shell())
manager.add_command('runserver', Debug())
manager.add_command('debug', Debug())
manager.add_command('urlmap', UrlMap())
manager.add_command('collectstatic', Collectstatic())
manager.add_command('makemessages', MakeMessages())
manager.add_command('compilemessages', CompileMessages())
manager.add_command('createsuperuser', CreateSuperUser())
manager.add_command('syncroles', SyncRoles())
manager.add_command('ensuredb', EnsureDb())
manager.add_command('db', MigrateCommand)
manager.add_command('createall', CreateAll())
manager.add_command('assets', ManageAssets(assets))
manager.add_command('clearcache', ClearCache())


if __name__ == '__main__':
    manager.run()
