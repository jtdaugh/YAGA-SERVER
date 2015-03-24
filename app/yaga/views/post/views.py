from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import RedirectView

from app.views import CrispyFilterView

from ...models import Post
from .filters import PostFilterSet


class PostBaseRedirectView(
    LoginRequiredMixin,
    RedirectView
):
    permanent = False
    query_string = True

    def get_redirect_url(self):
        return reverse_lazy('yaga:post:list')


class PostListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrispyFilterView,
    ListView
):
    paginate_by = 10
    template_name = 'yaga/post/list.html'
    raise_exception = True
    permission_required = 'posts.view_post'
    context_object_name = 'posts'
    filterset_class = PostFilterSet

    def get_queryset(self):
        return Post.objects.all()
