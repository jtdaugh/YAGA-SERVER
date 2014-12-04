from __future__ import absolute_import, division, unicode_literals

from flanker.addresslib import address
from flask.ext.babelex import lazy_gettext as _
from wtforms.validators import ValidationError, StopValidation


class BaseValidator(object):
    def __init__(self, message=None):
        if message is None:
            message = self.MESSAGE

        self.message = message

    @property
    def chain(self):
        return ValidationError(self.message)

    @property
    def stop(self):
        return StopValidation(self.message)

    def __call__(self, form, field):
        raise NotImplementedError


class DataRequired(BaseValidator):
    MESSAGE = _('This field is required.')

    def __call__(self, form, field):
        if not field.data:
            raise self.stop


class DNSMXEmail(BaseValidator):
    MESSAGE = _('Invalid email address.')

    def __call__(self, form, field):
        email = field.data

        if address.parse(email) is None:
            raise self.stop

        if address.validate_address(email) is None:
            raise self.stop
