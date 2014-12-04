from __future__ import absolute_import, division, unicode_literals

from flask import g
from flask.ext.babelex import lazy_gettext as _

from ...validators import BaseValidator
from .repository import user_storage, token_storage


class NotRegisteredUser(BaseValidator):
    MESSAGE = _('User already registered.')

    def __call__(self, form, field):
        if user_storage.get(
            email=field.data
        ):
            raise self.stop


class ValidActiveUser(BaseValidator):
    MESSAGE = _('Unknown user or password incorrect.')

    def __call__(self, form, field):
        user = user_storage.get(
            email=field.data
        )

        if user is None:
            raise self.stop

        if not user.is_active():
            raise self.stop

        if not user.verify_password(form.password.data):
            raise self.stop

        form.user = user


class UserToken(BaseValidator):
    MESSAGE = _('Unknown token.')

    def __call__(self, form, field):
        token = token_storage.get(
            token=field.data
        )

        if token is None:
            raise self.stop

        if token.user != g.user:
            raise self.stop
