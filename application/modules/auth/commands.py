from flask import current_app as app
from flask.ext.script import Command, prompt, prompt_pass
from werkzeug.datastructures import MultiDict

from .models import User, Role
from .forms import UserRegisterForm


class CreateSuperUser(Command):
    def run(self):
        superuser_role = Role.objects.get_or_create(
            name='superuser',
            description='superuser',
        )

        while True:
            email = prompt('email')
            password = prompt_pass('password')

            data = MultiDict()
            data['email'] = email
            data['password'] = password

            form = UserRegisterForm(data)

            if form.validate():
                user = User.create_user(
                    email=form.email.data,
                    password=form.password.data
                )
                user.roles = [superuser_role]
                user.save()

                break


class SyncRoles(Command):
    def run(self):
        for name, description in app.config['ROLES'].iteritems():
            if Role.objects.filter(name=name).count() == 0:
                role = Role()
                role.name = name
                role.name = description
                role.save()
