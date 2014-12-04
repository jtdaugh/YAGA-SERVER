from __future__ import absolute_import, division, unicode_literals

from flask import g
from flanker.addresslib import address
from flask.ext.babelex import lazy_gettext as _

from ...mixins import BaseValidator
from .repository import user_storage, token_storage


class DNSMXEmail(BaseValidator):
    MESSAGE = _('Invalid email address.')

    def __call__(self, form, field):
        email = field.data

        if address.parse(email) is None:
            raise self.stop

        if address.validate_address(email) is None:
            raise self.stop


class NotRegisteredUser(BaseValidator):
    MESSAGE = _('User already registered.')

    def __call__(self, form, field):
        if user_storage.get(
            email=field.data
        ):
            raise self.fail


class ValidActiveUser(BaseValidator):
    MESSAGE = _('Unknown user or password incorrect.')

    def __call__(self, form, field):
        user = user_storage.get(
            email=field.data
        )

        if user is None:
            raise self.stop

        if not user.is_active():
            raise self.fail

        if not user.verify_password(form.password.data):
            raise self.fail

        form.user = user


class UserToken(BaseValidator):
    MESSAGE = _('Unknown token.')

    def __call__(self, form, field):
        token = token_storage.get(
            token=field.data
        )

        if token is None:
            raise self.fail

        if token.user != g.user:
            raise self.fail
