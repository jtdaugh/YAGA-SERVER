from __future__ import absolute_import, division, unicode_literals

from wtforms.fields import TextField, PasswordField
from flask.ext.babelex import lazy_gettext as _

from ...forms import BaseForm
from ...validators import DataRequired, DNSMXEmail
from .validators import (
    NotRegisteredUser, ValidActiveUser, UserToken
)


class PasswordForm(BaseForm):
    password = PasswordField(
        _('Password'),
        validators=[
            DataRequired(),
        ]
    )


class UserLoginForm(PasswordForm):
    email = TextField(
        _('Email'),
        validators=[
            DataRequired(),
            DNSMXEmail(),
            ValidActiveUser()
        ]
    )


class UserRegisterForm(PasswordForm):
    email = TextField(
        _('Email'),
        validators=[
            DataRequired(),
            DNSMXEmail(),
            NotRegisteredUser()
        ]
    )


class TokenDeactivateForm(BaseForm):
    token = TextField(
        _('Token'),
        validators=[
            DataRequired(),
            UserToken()
        ]
    )
