from __future__ import absolute_import, division, unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class YagaAppConfig(AppConfig):
    name = 'yaga'
    verbose_name = _('Yaga')
