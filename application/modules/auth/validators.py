from flanker.addresslib import address
from flask.ext.babelex import lazy_gettext as _

from application.helpers import Validator, db
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
        if db.session.query(User).filter_by(
            email=field.data
        ).first() is not None:
            raise self.fail


class ValidActiveUser(Validator):
    MESSAGE = _('Unknown user or bad password.')

    def __call__(self, form, field):
        user = db.session.query(User).filter_by(
            email=field.data
        ).first()

        if user is None:
            raise self.fail

        if not user.is_active():
            raise self.fail

        if not user.verify_password(form.password.data):
            raise self.fail

        form.user = user
