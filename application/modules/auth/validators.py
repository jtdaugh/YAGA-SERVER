from __future__ import absolute_import, division, unicode_literals

from flask import g
from flask.ext.babelex import lazy_gettext as _

from ...validators import BaseValidator
from .repository import user_storage, token_storage


class ValidActiveUserValidator(BaseValidator):
    MESSAGE = _('Unknown user or password incorrect.')
    CODE = 'wrong_credentials'

    def validate(self, form, field):
        if form.password.errors:
            raise self.stop

        user = user_storage.get(
            phone=form.phone.data
        )

        if user is None:
            raise self.stop

        if not user.is_active():
            raise self.stop

        if not user.verify_password(form.password.data):
            raise self.stop

        form.obj = user


class UserTokenValidator(BaseValidator):
    MESSAGE = _('Unknown token.')

    def validate(self, form, field):
        token = token_storage.get(
            token=field.data,
        )

        if token is None:
            raise self.stop

        if token.user != g.user:
            raise self.stop
