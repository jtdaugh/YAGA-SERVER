from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Field, Fieldset, Layout, Submit
from django import forms
from django.utils.translation import ugettext_lazy as _

from ...models import Post


class Delete(
    Submit
):
    field_classes = 'btn btn-danger'


class PostForm(
    forms.ModelForm
):
    user = forms.CharField(label=_('User'))

    class Meta:
        model = Post
        fields = ('name', 'user', 'ready', 'deleted')

    @property
    def helper(self):
        helper = FormHelper()
        helper.layout = Layout(
            Fieldset(
                _('Change Post'),
                Field('name', disabled=True),
                Field('user', disabled=True),
                Field('ready', disabled=True),
                Field('deleted', disabled=True)
            ),
            ButtonHolder(
                Submit('submit', _('Save Post'))
            )
        )
        return helper
