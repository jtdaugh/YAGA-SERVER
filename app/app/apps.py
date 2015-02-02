from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_lazy as _

from .model_permissions import register_global_permission


class AppAppConfig(
    AppConfig
):
    name = 'app'
    verbose_name = _('App')

    def ready(self):
        from . import dispatch  # noqa # isort:skip

        post_migrate.connect(register_global_permission, sender=self)
