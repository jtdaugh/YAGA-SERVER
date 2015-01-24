from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.apps import apps
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from .conf import settings

_app_content_type = None


def get_app_content_type():
    global _app_content_type

    if _app_content_type is None:
        app = apps.get_app_config('app')
        _app_content_type, created = ContentType.objects.get_or_create(
            name=app.name,
            app_label=app.label
        )

    return _app_content_type


def register_permission(codename):
    name = 'can_{codename}'.format(
        codename=codename.replace('_', ' ')
    ).capitalize()

    permission, created = Permission.objects.get_or_create(
        content_type=get_app_content_type(),
        codename=codename,
        name=name
    )

    return Permission


def register_global_permission(sender, **kwargs):
    for permission in settings.GLOBAL_PERMISSIONS:
            register_permission(permission)
