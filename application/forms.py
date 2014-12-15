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


class BaseWebForm(BaseForm):
    API = False


class BaseApiForm(BaseForm):
    API = True
