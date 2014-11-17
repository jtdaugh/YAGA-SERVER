from flanker.addresslib import address
from flask.ext.babelex import lazy_gettext as _

from application.helpers import Validator
from .models import User


class DNSMXEmail(Validator):
    MESSAGE = _('Invalid email address.')

    def __call__(self, form, field):
        email = field.data

        if address.parse(email) is None:
            raise self.fail

        if address.validate_address(email) is None:
            raise self.fail


class NotRegisteredUser(Validator):
    MESSAGE = _('User already registered.')

    def __call__(self, form, field):
        if User.objects.filter(
            email=field.data
        ).count() != 0:
            raise self.fail


class ValidActiveUser(Validator):
    MESSAGE = _('Unknown user or bad password.')

    def __call__(self, form, field):
        try:
            user = User.objects.get(email=field.data)
        except User.DoesNotExist:
            raise self.fail

        if not user.is_active():
            raise self.fail

        if not user.verify_password(form.password.data):
            raise self.fail

        form.user = user
