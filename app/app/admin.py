from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)


class DisableNonSuperuserMixin(
    object
):
    def has_permission(self, request):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return self.has_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_permission(request)

    def has_module_permission(self, request):
        return self.has_permission(request)
