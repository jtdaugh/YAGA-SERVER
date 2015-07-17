from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Field, Fieldset, Layout, Submit
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _


class UserForm(
    forms.ModelForm
):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['is_monkey'].initial = self.instance.is_monkey

    is_monkey = forms.BooleanField(
        label=_('Monkey'),
        help_text=_('Can sign in without verification code verification'),
        required=False
    )

    def save(self, commit=True):
        self.instance.is_monkey = self.cleaned_data['is_monkey']

        return super(UserForm, self).save(commit=commit)

    class Meta:
        model = get_user_model()
        fields = ('name', 'phone', 'is_active', 'is_monkey')

    @property
    def helper(self):
        helper = FormHelper()
        helper.layout = Layout(
            Fieldset(
                _('Update User'),
                Field('name'),
                Field('phone', readonly=True),
                Field('is_active'),
                Field('is_monkey'),
            ),
            ButtonHolder(
                Submit('submit', _('Save User'))
            )
        )
        return helper
