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
    class Meta:
        model = get_user_model()
        fields = ('name', 'phone', 'is_active',)

    @property
    def helper(self):
        helper = FormHelper()
        helper.layout = Layout(
            Fieldset(
                _('Change User'),
                Field('name'),
                Field('phone', readonly=True),
                Field('is_active')
            ),
            ButtonHolder(
                Submit('submit', _('Save User'))
            )
        )
        return helper
