from __future__ import absolute_import, division, unicode_literals

from flask import g, request
from flask.ext.babelex import lazy_gettext as _

from ...validators import BaseValidator
from ...helpers import phone
from ...utils import now
from .repository import user_storage, token_storage, code_storage


class ValidActiveUserValidator(BaseValidator):
    MESSAGE = _('Unknown user.')
    JSON_MESSAGE = 'unknown_user'

    def validate(self, form, field):
        if form.code.errors:
            raise self.stop

        user = user_storage.get(
            phone=form.phone.data
        )

        if user is None:
            raise self.stop

        if not user.is_active():
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


class VerificationCodeValidator(BaseValidator):
    MESSAGE = _('Malformed code.')
    JSON_MESSAGE = 'malformed_code'

    def validate(self, form, field):
        if not 4 <= len(field.data) <= 6:
            raise self.stop

        try:
            int(field.data)
        except:
            raise self.stop


class ValidVerificationCodeValidator(BaseValidator):
    MESSAGE = _('Invalid code.')
    JSON_MESSAGE = 'invalid_code'

    def validate(self, form, field):
        code = code_storage.get_latest_code(form.phone.data)

        if not code:
            raise self.stop

        is_valid_code = phone.check_verify(
            code.request_id, field.data,
            ip=request.remote_addr
        )

        if not is_valid_code:
            raise self.stop
        else:
            code_storage.mark_as_validated(code)


class ConcurrentRequestValidator(BaseValidator):
    MESSAGE = _('Concurrent code request.')
    JSON_MESSAGE = 'concurrent_request'

    def validate(self, form, field):
        code = code_storage.get_latest_code(form.phone.data)

        if code:
            if not code.validated and code.expire_at > now():
                raise self.stop
