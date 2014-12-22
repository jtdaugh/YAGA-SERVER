from __future__ import absolute_import, division, unicode_literals

from flask_wtf import Form
from flask.ext.babelex import lazy_gettext as _


class Translations(object):
    def gettext(self, string):
        return _(string)

    def ngettext(self, singular, plural, n):
        raise NotImplementedError


class BaseForm(Form):
    translations = Translations()

    def _get_translations(self):
        return self.translations

    def validate(self):
        is_valid = super(Form, self).validate()

        if is_valid:
            return self.validate_form()
        else:
            return False

    def validate_form(self):
        clean = self.clean()

        return True

    def clean(self):
        pass


class BaseWebForm(BaseForm):
    API = False


class BaseApiForm(BaseForm):
    API = True
