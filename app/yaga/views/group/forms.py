from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from django import forms
from django.utils.translation import ugettext_lazy as _


class Delete(
    Submit
):
    field_classes = 'btn btn-danger'


class WipeForm(
    forms.Form
):
    @property
    def helper(self):
        helper = FormHelper()
        helper.layout = Layout(
            Fieldset(
                _('Are You sure want to wipe group?'),
            ),
            ButtonHolder(
                Delete('submit', _('Yes, Kick all members'))
            )
        )
        return helper
