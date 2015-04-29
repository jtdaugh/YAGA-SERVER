from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.base import RedirectView

from app.views import CrispyFilterView

from ...models import Group
from .filters import GroupFilterSet


class GroupView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
):
    raise_exception = True
    permission_required = 'posts.view_group'

    def get_queryset(self):
        return Group.objects.all()


class GroupBaseRedirectView(
    GroupView,
    RedirectView
):
    permanent = False
    query_string = True

    def get_redirect_url(self):
        return reverse_lazy('yaga:group:list')


class GroupListView(
    GroupView,
    CrispyFilterView,
    ListView
):
    paginate_by = 25
    template_name = 'yaga/group/list.html'
    context_object_name = 'groups'
    filterset_class = GroupFilterSet

    def get_queryset(self):
        return super(
            GroupListView, self
        ).get_queryset().order_by('-created_at')


class GroupDetailView(
    GroupView,
    DetailView
):
    context_object_name = 'group'
    pk_url_kwarg = 'group_id'
    template_name = 'yaga/group/detail.html'
