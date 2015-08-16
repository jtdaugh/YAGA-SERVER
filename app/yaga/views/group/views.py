from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView, UpdateView

from app.views import CrispyFilterView

from ...models import Group
from .filters import GroupFilterSet
from .forms import WipeForm, GroupDetailForm


class GroupView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
):
    raise_exception = True
    permission_required = 'yaga.view_group'

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
    UpdateView
):
    permission_required = 'yaga.change_group'
    pk_url_kwarg = 'group_id'
    template_name = 'yaga/group/detail.html'
    context_object_name = 'group'
    form_class = GroupDetailForm

    def form_valid(self, form):
        form.instance.namer = self.request.user
        return super(GroupDetailView, self).form_valid(form)
   
    def get_context_data(self, **kwargs):
        context = super(GroupDetailView, self).get_context_data(**kwargs)
        context['form'] = self.form_class()
        return context

    def get_success_url(self):
        return reverse_lazy('yaga:group:detail', kwargs={
            'group_id': self.object.pk
        })



class GroupWipeDeleteView(
    GroupView,
    DeleteView
):
    context_object_name = 'group'
    pk_url_kwarg = 'group_id'
    permission_required = 'yaga.wipe_group'
    form_class = WipeForm
    template_name = 'yaga/group/wipe.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        for member in self.object.member_set.all():
            member.delete()

        success_url = self.get_success_url()

        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse_lazy(
            'yaga:group:detail',
            kwargs={
                'group_id': self.object.pk
            }
        )

    def get_context_data(self, **kwargs):
        context = super(GroupWipeDeleteView, self).get_context_data(**kwargs)
        context['form'] = self.form_class()
        return context
