from __future__ import absolute_import, division, unicode_literals

from flask import g
from flask.ext.babelex import lazy_gettext as _

from ...validators import BaseValidator, UniqueValidator
from .repository import user_storage, token_storage


class UniquePhoneValidator(UniqueValidator):
    STORAGE = user_storage
    FIELD = 'phone'
    MESSAGE = _('Phone is already registered.')


class UniqueNameValidator(UniqueValidator):
    STORAGE = user_storage
    FIELD = 'name'
    MESSAGE = _('Name is already registered.')


class ValidActiveUserValidator(BaseValidator):
    FIELD = 'phone'
    MESSAGE = _('Unknown user or password incorrect.')

    def __call__(self, form, field):
        user = user_storage.get(
            **self.query(field.data)
        )

        if user is None:
            raise self.stop

        if not user.is_active():
            raise self.stop

        if not user.verify_password(form.password.data):
            raise self.stop

        form.obj = user


class UserTokenValidator(BaseValidator):
    FIELD = 'token'
    MESSAGE = _('Unknown token.')

    def __call__(self, form, field):
        token = token_storage.get(
            **self.query(field.data)
        )

        if token is None:
            raise self.stop

        if token.user != g.user:
            raise self.stop


class CurrentTokenValidator(BaseValidator):
    MESSAGE = _('Wrong token.')

    def __call__(self, form, field):
        if field.data != g.token:
            raise self.stop
