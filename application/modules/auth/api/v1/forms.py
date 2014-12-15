from __future__ import absolute_import, division, unicode_literals

from wtforms.fields import TextField
from flask.ext.babelex import lazy_gettext as _

from ...forms import PasswordForm, UserLoginForm
from .....validators import DataRequiredValidator, PhoneValidator
from .....forms import BaseApiForm
from .validators import (
    CurrentTokenValidator, AvailablePhoneValidator, AvailableNameValidator
)


class UserRegisterApiForm(BaseApiForm, PasswordForm):
    phone = TextField(
        _('Phone'),
        validators=[
            DataRequiredValidator(),
            PhoneValidator(),
            AvailablePhoneValidator()
        ]
    )

    name = TextField(
        _('Name'),
        validators=[
            DataRequiredValidator(),
            AvailableNameValidator()
        ]
    )


class UserLoginApiForm(BaseApiForm, UserLoginForm):
    pass


class UserLogoutApiForm(BaseApiForm):
    token = TextField(
        _('Token'),
        validators=[
            DataRequiredValidator(),
            CurrentTokenValidator()
        ]
    )
