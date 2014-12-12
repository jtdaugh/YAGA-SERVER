from __future__ import absolute_import, division, unicode_literals

from wtforms.fields import TextField, PasswordField
from flask.ext.babelex import lazy_gettext as _

from ...forms import BaseForm
from ...validators import DataRequiredValidator, PhoneValidator
from .validators import (
    UniquePhoneValidator, UniqueNameValidator, ValidActiveUserValidator,
    UserTokenValidator, CurrentTokenValidator
)


class PasswordForm(BaseForm):
    password = PasswordField(
        _('Password'),
        validators=[
            DataRequiredValidator(),
        ]
    )


class UserLoginForm(PasswordForm):
    phone = TextField(
        _('Phone'),
        validators=[
            DataRequiredValidator(),
            PhoneValidator(),
            ValidActiveUserValidator()
        ]
    )


class UserRegisterForm(PasswordForm):
    phone = TextField(
        _('Phone'),
        validators=[
            DataRequiredValidator(),
            PhoneValidator(),
            UniquePhoneValidator()
        ]
    )

    name = TextField(
        _('Name'),
        validators=[
            DataRequiredValidator(),
            UniqueNameValidator()
        ]
    )


class UserLogoutForm(BaseForm):
    token = TextField(
        _('Token'),
        validators=[
            DataRequiredValidator(),
            CurrentTokenValidator()
        ]
    )


class TokenDeactivateForm(BaseForm):
    token = TextField(
        _('Token'),
        validators=[
            DataRequiredValidator(),
            UserTokenValidator()
        ]
    )
