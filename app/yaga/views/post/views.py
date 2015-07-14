from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import uuid

from braces.views import (
    JSONResponseMixin, LoginRequiredMixin, PermissionRequiredMixin
)
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import DeleteView, ListView
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView

from app.views import CrispyFilterView

from ...models import Post
from .filters import PostFilterSet
from .forms import ApproveForm, PageDeleteForm


class PostView(
    LoginRequiredMixin,
    PermissionRequiredMixin
):
    raise_exception = True
    permission_required = 'yaga.view_post'

    def get_queryset(self):
        return Post.objects.all()


class PostBaseRedirectView(
    PostView,
    RedirectView
):
    permanent = False
    query_string = True

    def get_redirect_url(self):
        return reverse_lazy('yaga:post:list')


class PostListView(
    PostView,
    CrispyFilterView,
    ListView
):
    paginate_by = 25
    template_name = 'yaga/post/list.html'
    context_object_name = 'posts'
    filterset_class = PostFilterSet

    def get_queryset(self):
        return super(
            PostListView, self
        ).get_queryset().order_by('-created_at')


class PostDeleteView(
    PostView,
    DeleteView
):
    pk_url_kwarg = 'post_id'
    template_name = 'yaga/post/delete.html'
    permission_required = 'yaga.delete_post'
    context_object_name = 'post'
    form_class = PageDeleteForm

    def get_success_url(self):
        return reverse_lazy('yaga:post:list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.mark_deleted()
        return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super(PostDeleteView, self).get_context_data(**kwargs)
        context['form'] = self.form_class()
        return context


class PostApproveFormView(
    PostView,
    JSONResponseMixin,
    FormView
):
    permission_required = 'yaga.approve_post'
    form_class = ApproveForm

    def form_valid(self, form):
        pk = form.cleaned_data['pk']

        pk = uuid.UUID(pk)

        post = Post.objects.filter(
            pk=pk
        ).first()

        if post:
            post = post.mark_approved()

        approved = post and post.approved

        return self.render_json_response({
            'approved': approved
        })
