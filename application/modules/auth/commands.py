from __future__ import absolute_import, division, unicode_literals

from flask import current_app as app
from flask.ext.script import Command, prompt, prompt_pass
from werkzeug.datastructures import MultiDict

from .forms import UserRegisterForm
from .repository import role_storage, user_storage


class CreateSuperUser(Command):
    def run(self):
        superuser_role = role_storage.get_or_create(
            'superuser'
        )

        while True:
            data = MultiDict()
            data['email'] = prompt('email')
            data['password'] = prompt_pass('password')

            form = UserRegisterForm(data)

            if form.validate():
                user = user_storage.create(
                    form.email.data,
                    form.password.data
                )
                user_storage.add_role(user, superuser_role)

                break


class SyncRoles(Command):
    def run(self):
        for name in app.config['ROLES']:
            role_storage.get_or_create(
                name
            )
