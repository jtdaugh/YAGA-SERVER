from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib.auth.models import Permission

from rest_framework import status as http_status


class BasePermissionContext(
    object
):
    def wipe_user_perm_cache(self, user):
        if hasattr(user, '_perm_cache'):
            delattr(user, '_perm_cache')

    def ensure_permission(self, permission):
        if not isinstance(permission, Permission):
            permission = Permission.objects.get(
                codename=permission
            )

        return permission

    def grant_permission(self, user=None, permission=None):
        if None in (user, permission):
            user = self.user
            permission = self.permission

        print self.ensure_permission(permission)

        self.user.user_permissions.add(self.ensure_permission(permission))
        self.wipe_user_perm_cache(user)

    def revoke_permission(self, user=None, permission=None):
        if None in (user, permission):
            user = self.user
            permission = self.permission

        user.user_permissions.remove(self.ensure_permission(permission))
        self.wipe_user_perm_cache(user)

    def __exit__(self, *args, **kwargs):
        self.revoke_permission()


class UserPermissionContext(
    BasePermissionContext
):
    def __init__(
        self, user, permission
    ):
        self.user = user

        self.permission = permission

    def __enter__(self):
        self.grant_permission()


class ViewPermissionContext(
    BasePermissionContext
):
    def __init__(
        self,
        fn, permission, base=None,
        user=None, status=None, callback=None
    ):
        self.fn = fn

        if not isinstance(permission, Permission):
            permission = Permission.objects.get(
                codename=permission
            )

        self.permission = permission

        self.base = base

        if user is None:
            user = base.user

        self.user = user

        if status is None:
            status = http_status.HTTP_403_FORBIDDEN

        self.status = status

        if callback is None:
            callback = self.base.assertEqual

        self.callback = callback

    def __enter__(self):
        response = self.fn()

        self.callback(response.status_code, self.status)

        self.grant_permission(self.user, self.permission)

        response = self.fn()

        return response
