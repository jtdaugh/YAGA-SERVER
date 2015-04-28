from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, UpdateView
from django.views.generic.base import RedirectView

from app.views import CrispyFilterView

from ...models import Post
from .filters import PostFilterSet
from .forms import PostForm


class PostView(
    LoginRequiredMixin,
    PermissionRequiredMixin
):
    raise_exception = True
    permission_required = 'posts.view_post'


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
        return Post.objects.all().order_by('-created_at')


class PostUpdateView(
    PostView,
    UpdateView
):
    pk_url_kwarg = 'post_id'
    template_name = 'yaga/post/detail.html'
    permission_required = 'yaga.change_post'
    form_class = PostForm
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.all()

    def get_success_url(self):
        return reverse_lazy('yaga:post:detail', kwargs={
            'post_id': self.object.pk
        })
