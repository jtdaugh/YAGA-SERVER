from __future__ import absolute_import, division, unicode_literals


from rest_framework.permissions import BasePermission

from accounts.models import Token


class CanDestroyToken(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return request.auth and isinstance(request.auth, Token)

        return True
