from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib.auth.models import Permission
from django.test import TestCase

from ..conf import settings


class AppPermissionsTestCase(
    TestCase
):
    def test_app_permissions(self):
        for permission in settings.GLOBAL_PERMISSIONS:
            self.assertIsNotNone(Permission.objects.filter(
                codename=permission
            ).first())
