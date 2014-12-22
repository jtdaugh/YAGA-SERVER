from __future__ import absolute_import, division, unicode_literals

from wtforms.fields import StringField
from flask.ext.babelex import lazy_gettext as _

from .....validators import DataRequiredValidator, PhoneValidator
from .....forms import BaseApiForm
from ...forms import UserLoginForm, CodeRequestForm, CodeForm
from .validators import CurrentTokenValidator, AvailablePhoneValidator


class PhoneApiForm(BaseApiForm):
    phone = StringField(
        _('Phone'),
        validators=[
            DataRequiredValidator(),
            PhoneValidator(),
        ]
    )


class UserRegisterApiForm(BaseApiForm, CodeForm):
    phone = StringField(
        _('Phone'),
        validators=[
            DataRequiredValidator(),
            PhoneValidator(),
            AvailablePhoneValidator()
        ]
    )


class UserLoginApiForm(BaseApiForm, UserLoginForm):
    pass


class CodeRequestApiForm(BaseApiForm, CodeRequestForm):
    pass


class UserLogoutApiForm(BaseApiForm):
    token = StringField(
        _('Token'),
        validators=[
            DataRequiredValidator(),
            CurrentTokenValidator()
        ]
    )
