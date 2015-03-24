from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import RedirectView

from app.views import CrispyFilterView

from .filters import UserFilterSet


class UserBaseRedirectView(
    LoginRequiredMixin,
    RedirectView
):
    permanent = False
    query_string = True

    def get_redirect_url(self):
        return reverse_lazy('yaga:user:list')


class UserListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrispyFilterView,
    ListView
):
    paginate_by = 50
    template_name = 'yaga/user/list.html'
    raise_exception = True
    permission_required = 'accounts.view_user'
    context_object_name = 'users'
    filterset_class = UserFilterSet

    def get_queryset(self):
        return get_user_model().objects.all()
