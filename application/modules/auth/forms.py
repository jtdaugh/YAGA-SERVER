from wtforms import validators
from wtforms.fields import TextField, PasswordField
from flask.ext.babelex import lazy_gettext as _

from application.helpers import Form
from .validators import DNSMXEmail, NotRegisteredUser, ValidActiveUser


class PasswordForm(Form):
    password = PasswordField(
        'password',
        validators=[
            validators.InputRequired(_('This field is required.')),
        ]
    )


class UserLoginForm(PasswordForm):
    email = TextField(
        'email',
        validators=[
            validators.InputRequired(_('This field is required.')),
            validators.Email(_('Invalid email address.')),
            ValidActiveUser()
        ]
    )


class UserRegisterForm(PasswordForm):
    email = TextField(
        'email',
        validators=[
            validators.InputRequired(_('This field is required.')),
            DNSMXEmail(),
            NotRegisteredUser()
        ]
    )
