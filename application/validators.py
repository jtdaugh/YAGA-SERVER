from __future__ import absolute_import, division, unicode_literals

from flanker.addresslib import address
from flask.ext.babelex import lazy_gettext as _
from wtforms.validators import ValidationError, StopValidation

from .utils import phone_tools


class BaseValidator(object):
    MESSAGE = _('General error.')
    JSON_MESSAGE = 'general'

    def __init__(self, message=None, json_message=None):
        if message is None:
            message = self.MESSAGE

        if json_message is None:
            json_message = self.JSON_MESSAGE

        self.message = message

        self.json_message = json_message

    @property
    def chain(self):
        return ValidationError(self.output)

    @property
    def stop(self):
        return StopValidation(self.output)

    def __call__(self, form, field):
        if form.API:
            self.output = self.json_message
        else:
            self.output = self.message

        return self.validate(form, field)

    def validate(self, form, field):
        raise NotImplementedError


class DataRequiredValidator(BaseValidator):
    MESSAGE = _('This field is required.')
    JSON_MESSAGE = 'required'

    def validate(self, form, field):
        if not field.data:
            raise self.stop


class EmailValidator(BaseValidator):
    MESSAGE = _('Invalid email address.')
    JSON_MESSAGE = 'invalid_email'

    def validate(self, form, field):
        email = field.data

        if address.parse(email) is None:
            raise self.stop

        if address.validate_address(email) is None:
            raise self.stop


class PhoneValidator(BaseValidator):
    MESSAGE = _('Invalid phone number.')
    JSON_MESSAGE = 'invalid_phone'

    def validate(self, form, field):
        number = field.data

        number = phone_tools.format_E164(number)

        if number is None:
            raise self.stop

        field.data = number
