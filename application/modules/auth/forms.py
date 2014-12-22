from __future__ import absolute_import, division, unicode_literals

from wtforms.fields import StringField, PasswordField
from flask.ext.babelex import lazy_gettext as _

from ...forms import BaseWebForm, BaseForm
from ...validators import DataRequiredValidator, PhoneValidator
from .validators import (
    ValidActiveUserValidator, UserTokenValidator,
    VerificationCodeValidator, ValidVerificationCodeValidator,
    ConcurrentRequestValidator
)


class CodeForm(BaseForm):
    code = PasswordField(
        _('Code'),
        # validators=[
        #     DataRequiredValidator(),
        #     VerificationCodeValidator(),
        #     ValidVerificationCodeValidator()
        # ]
    )


class CodeRequestForm(BaseForm):
    phone = StringField(
        _('Phone'),
        validators=[
            DataRequiredValidator(),
            PhoneValidator(),
            ConcurrentRequestValidator()
        ]
    )


class UserLoginForm(CodeForm):
    phone = StringField(
        _('Phone'),
        validators=[
            DataRequiredValidator(),
            PhoneValidator(),
            ValidActiveUserValidator()
        ]
    )


class UserLoginWebForm(BaseWebForm, UserLoginForm):
    pass


class CodeRequestWebForm(BaseWebForm, CodeRequestForm):
    pass


class TokenDeactivateWebForm(BaseWebForm):
    token = StringField(
        _('Token'),
        validators=[
            DataRequiredValidator(),
            UserTokenValidator()
        ]
    )
