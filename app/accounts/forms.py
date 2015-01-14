from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm, ReadOnlyPasswordHashField
)
from django.utils.translation import ugettext_lazy as _


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
        helper.add_input(Submit('submit', _('Sign in')))

        return helper
