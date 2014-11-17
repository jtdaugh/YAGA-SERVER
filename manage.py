#!/usr/bin/env python
import os
import json
from urllib import unquote

import flask_s3
import envoy
from flask.ext.script import Command
from IPython import embed
from babel import support


from application.core import app
from application.helpers import db
from application.modules.auth.commands import CreateSuperUser
from application.modules.auth.commands import SyncRoles


class Shell(Command):
    @property
    def context(self):
        return {
            'app': app
        }

    def run(self):
        embed(user_ns=self.context)


class RunServer(Command):
    def run(self):
        app.run(
            host=app.config['APP_HOST'],
            port=app.config['APP_PORT'],
            debug=True,
            use_debugger=True,
            use_reloader=True
        )


class UrlMap(Command):
    def run(self):
        output = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            line = unquote(
                '{:50s} {:20s} {}'.format(rule.endpoint, methods, rule)
            )
            output.append(line)

        for line in sorted(output):
            print(line)


class Collectstatic(Command):
    def run(self):
        flask_s3.create_all(app)


class ShellMixin(object):
    def local(self, cmd):
        shell = envoy.run(cmd)

        if shell.status_code != 0:
            print(shell.std_err)
            raise RuntimeError


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


class CreateAll(Command):
    def run(self):
        db.create_all()
        db.session.commit()


app.manager.add_command('shell', Shell())
app.manager.add_command('runserver', RunServer())
app.manager.add_command('urlmap', UrlMap())
app.manager.add_command('collectstatic', Collectstatic())
app.manager.add_command('makemessages', MakeMessages())
app.manager.add_command('compilemessages', CompileMessages())
app.manager.add_command('createsuperuser', CreateSuperUser())
app.manager.add_command('syncroles', SyncRoles())
app.manager.add_command('createall', CreateAll())


if __name__ == '__main__':
    app.manager.run()
