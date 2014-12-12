from __future__ import absolute_import, division, unicode_literals

from flanker.addresslib import address
from flask.ext.babelex import lazy_gettext as _
from wtforms.validators import ValidationError, StopValidation

from .utils import phone_tools


class BaseValidator(object):
    def __init__(self, message=None):
        if message is None:
            message = self.MESSAGE

        self.message = message

    def query(self, data):
        return {
            self.FIELD: data
        }

    @property
    def chain(self):
        return ValidationError(self.message)

    @property
    def stop(self):
        return StopValidation(self.message)

    def __call__(self, form, field):
        raise NotImplementedError


class UniqueValidator(BaseValidator):
    def __call__(self, form, field):
        obj = self.STORAGE.get(
            **self.query(field.data)
        )

        if obj:
            raise self.stop


class DataRequiredValidator(BaseValidator):
    MESSAGE = _('This field is required.')

    def __call__(self, form, field):
        if not field.data:
            raise self.stop


class EmailValidator(BaseValidator):
    MESSAGE = _('Invalid email address.')

    def __call__(self, form, field):
        email = field.data

        if address.parse(email) is None:
            raise self.stop

        if address.validate_address(email) is None:
            raise self.stop


class PhoneValidator(BaseValidator):
    MESSAGE = _('Invalid phone number.')

    def __call__(self, form, field):
        number = field.data

        number = phone_tools.format(number)

        if number is None:
            raise self.stop

        field.data = number
