from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from app.utils import reverse_host
from app.views import CacheView, UserCacheView
from yaga.models import Post
import uuid

from .conf import settings


class FaviconRedirectView(
    CacheView,
    RedirectView
):
    permanent = False
    query_string = False

    def get_redirect_url(self):
        return static(settings.FAVICON_STATIC)


class RobotsTemplateView(
    CacheView,
    TemplateView
):
    template_name = 'content/robots.txt'
    content_type = 'text/plain'

    def get_context_data(self, **kwargs):
        context = super(RobotsTemplateView, self).get_context_data(**kwargs)
        context['sitemap_url'] = reverse_host('sitemap')
        return context


class IndexTemplateView(
    TemplateView
):
    template_name = 'content/index.html'

class WatchVideoView(
    TemplateView
):
    template_name = 'content/watch.html'

    def get_context_data(self, **kwargs):
        context = super(WatchVideoView, self).get_context_data(**kwargs)

        # filter UUID based on http://svn.python.org/projects/python/branches/pep-0384/Lib/uuid.py

        short_id = self.kwargs['post_short_id']

        low_bound = uuid.UUID(short_id + "000000000000000000000000")
        high_bound = uuid.UUID(short_id + "FFFFFFFFFFFFFFFFFFFFFFFF")

        for p in Post.objects.select_related('user').filter(
            pk__gte=low_bound,
            pk__lte=high_bound
        ):
            if str(p.id).startswith(self.kwargs['post_short_id']):
                context['post'] = p
                context['username'] = p.user.name
                break;
            
        return context


