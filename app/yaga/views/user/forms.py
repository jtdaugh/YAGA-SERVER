from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Submit, Layout


class Delete(
    Submit
):
    field_classes = 'btn btn-danger'


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
            'name',
            Field('phone', readonly=False),
            'is_active',
        )
        helper.add_input(Submit('submit', _('Save User')))
        return helper
