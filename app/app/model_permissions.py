from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import django
from django.apps import apps
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from .conf import settings
from .utils import once

_app_content_type = None


def get_app_content_type():
    global _app_content_type

    if _app_content_type is None:
        app = apps.get_app_config('app')

        query = {
            'app_label': app.label
        }

        if django.VERSION[:2] >= (1, 8):
            name_field = 'model'
        else:
            name_field = 'name'

        query[name_field] = app.name

        _app_content_type, created = ContentType.objects.get_or_create(
            **query
        )

    return _app_content_type


def register_permission(codename):
    name = 'Can {codename}'.format(
        codename=codename.replace('_', ' ')
    )

    permission, created = Permission.objects.get_or_create(
        content_type=get_app_content_type(),
        codename=codename,
        name=name
    )

    return Permission


@once
def register_global_permission(sender, **kwargs):
    for permission in settings.GLOBAL_PERMISSIONS:
            register_permission(permission)
