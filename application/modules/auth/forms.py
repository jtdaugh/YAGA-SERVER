from __future__ import absolute_import, division, unicode_literals

from wtforms import validators
from wtforms.fields import TextField, PasswordField
from flask.ext.babelex import lazy_gettext as _

from ...mixins import BaseForm
from .validators import (
    DNSMXEmail, NotRegisteredUser, ValidActiveUser, UserToken
)


class PasswordForm(BaseForm):
    password = PasswordField(
        _('Password'),
        validators=[
            validators.InputRequired(_('This field is required.')),
        ]
    )


class UserLoginForm(PasswordForm):
    email = TextField(
        _('Email'),
        validators=[
            validators.InputRequired(_('This field is required.')),
            validators.Email(_('Invalid email address.')),
            ValidActiveUser()
        ]
    )


class UserRegisterForm(PasswordForm):
    email = TextField(
        _('Email'),
        validators=[
            validators.InputRequired(_('This field is required.')),
            DNSMXEmail(),
            NotRegisteredUser()
        ]
    )


class TokenDeactivateForm(BaseForm):
    token = TextField(
        _('Token'),
        validators=[
            validators.InputRequired(_('This field is required.')),
            UserToken()
        ]
    )
