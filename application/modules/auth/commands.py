from __future__ import absolute_import, division, unicode_literals

from flask import current_app as app
from flask.ext.script import Command, prompt, prompt_pass
from werkzeug.datastructures import MultiDict

from ...helpers import db
from .models import Role
from .forms import UserRegisterForm


class CreateSuperUser(Command):
    def run(self):
        superuser_role = db.session.query(Role).filter_by(
            name='superuser'
        ).first()

        if superuser_role is None:
            superuser_role = Role(
                name='superuser',
                description=app.config['ROLES']['superuser']
            )

            db.session.add(superuser_role)
            db.session.commit()

        while True:
            email = prompt('email')
            password = prompt_pass('password')

            data = MultiDict()
            data['email'] = email
            data['password'] = password

            form = UserRegisterForm(data)

            if form.validate():
                user = app.user_datastore.create_user(
                    email=email,
                )
                user.set_password(password)
                app.user_datastore.add_role_to_user(user, superuser_role)

                db.session.commit()

                break


class SyncRoles(Command):
    def run(self):
        for name, description in app.config['ROLES'].iteritems():
            if db.session.query(Role).filter_by(
                name=name
            ).first() is None:
                role = Role(
                    name=name,
                    description=description
                )

                db.session.add(role)
                db.session.commit()
