from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Field
from django import forms
from django.contrib.auth import get_user_model, _clean_credentials
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, ReadOnlyPasswordHashField
)
from django.contrib.auth.signals import user_login_failed
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext

from .conf import settings


class UserCreationForm(
    forms.ModelForm
):
    error_messages = {
        'password_mismatch': _('The two password fields didn\'t match.'),
    }

    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput
    )

    password2 = forms.CharField(
        label=_('Password confirmation'),
        widget=forms.PasswordInput,
        help_text=_('Enter the same password as above, for verification.')
    )

    class Meta:
        model = get_user_model()
        exclude = ()

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()

        return user

    def clean_name(self):
        name = self.cleaned_data['name']

        if not name:
            return None

        return name

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch'
            )

        return password2


class UserChangeForm(
    forms.ModelForm
):
    password = ReadOnlyPasswordHashField(
        label=_('Password'),
        help_text=_(
            'Raw passwords are not stored, so there is no way to see '
            'this user\'s password, but you can change the password '
            'using <a href=\'password/\'>this form</a>.'
        )
    )

    class Meta:
        model = get_user_model()
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_name(self):
        name = self.cleaned_data['name']

        if not name:
            return None

        return name

    def clean_password(self):
        return self.initial['password']


class SignInForm(
    AuthenticationForm
):
    @property
    def helper(self):
        helper = FormHelper()
        helper.layout = Layout(
            Fieldset(
                _('Sign In'),
                Field('username'),
                Field('password')
            ),
            ButtonHolder(
                Submit('submit', _('Sign in'))
            )
        )

        return helper


class ChangePasswordForm(
    PasswordChangeForm
):
    error_messages = dict(PasswordChangeForm.error_messages, **{
        'same_password': _('Please enter another password.'),
        'short_password': ungettext(
            'Password must have at least {count} character.',
            'Password must have at least {count} characters.',
            settings.ACCOUNTS_MIN_PASSWORD_LEN
        ).format(
            count=settings.ACCOUNTS_MIN_PASSWORD_LEN
        )
    })

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')

        if self.user.check_password(password1):
            raise forms.ValidationError(
                self.error_messages['same_password'],
                code='same_password'
            )

        if len(password1) < settings.ACCOUNTS_MIN_PASSWORD_LEN:
            raise forms.ValidationError(
                self.error_messages['short_password'],
                code='short_password'
            )

        return password1

    def clean_old_password(self):
        try:
            return super(ChangePasswordForm, self).clean_old_password()
        except forms.ValidationError as e:
            user_login_failed.send(__name__, credentials=_clean_credentials({
                'username': getattr(
                    self.user, get_user_model().USERNAME_FIELD
                ),
                'password': self.cleaned_data['old_password']
            }))
            raise e

    @property
    def helper(self):
        helper = FormHelper()

        helper.layout = Layout(
            Fieldset(
                _('Change Password'),
                Field('old_password'),
                Field('new_password1'),
                Field('new_password2'),
            ),
            ButtonHolder(
                Submit('submit', _('Change password'))
            )
        )

        return helper
