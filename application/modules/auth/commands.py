from __future__ import (
    absolute_import, division, unicode_literals, print_function
)

from flask import current_app as app
from flask.ext.script import Command, prompt, prompt_pass
from werkzeug.datastructures import MultiDict

from .forms import UserRegisterForm
from .repository import role_storage, user_storage


class CreateSuperUser(Command):
    def run(self):
        while True:
            data = MultiDict()
            data['phone'] = prompt('phone')
            data['name'] = prompt('name')
            data['password'] = prompt_pass('password')

            form = UserRegisterForm(data, csrf_enabled=False)

            if form.validate():
                user = user_storage.create(
                    phone=form.phone.data,
                    name=form.name.data,
                    password=form.password.data
                )
                user_storage.add_role(user, 'superuser')

                break
            else:
                print(form.errors)


class SyncRoles(Command):
    def run(self):
        for name in app.config['ROLES']:
            role_storage.get_or_create(
                name=name
            )
