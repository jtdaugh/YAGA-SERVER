from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, UpdateView
from django.views.generic.base import RedirectView

from app.views import CrispyFilterView

from .filters import UserFilterSet
from .forms import UserForm


class UserView(
    LoginRequiredMixin,
    PermissionRequiredMixin
):
    raise_exception = True
    permission_required = 'accounts.view_user'

    def get_queryset(self):
        return get_user_model().objects.all()


class UserBaseRedirectView(
    UserView,
    RedirectView
):
    permanent = False
    query_string = True

    def get_redirect_url(self):
        return reverse_lazy('yaga:user:list')


class UserListView(
    UserView,
    CrispyFilterView,
    ListView
):
    paginate_by = 25
    template_name = 'yaga/user/list.html'
    context_object_name = 'users'
    filterset_class = UserFilterSet

    def get_queryset(self):
        return super(
            UserListView, self
        ).get_queryset().order_by('-date_joined')


class UserUpdateView(
    UserView,
    UpdateView
):
    pk_url_kwarg = 'user_id'
    template_name = 'yaga/user/update.html'
    permission_required = 'accounts.change_user'
    form_class = UserForm
    context_object_name = 'user'

    def get_success_url(self):
        return reverse_lazy('yaga:user:detail', kwargs={
            'user_id': self.object.pk
        })
