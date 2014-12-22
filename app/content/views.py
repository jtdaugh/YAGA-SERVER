from __future__ import absolute_import, division, unicode_literals

from django.views.generic import TemplateView
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.views.generic.base import RedirectView
from django.conf import settings

from app.views import CacheView, UserCacheView
from app.utils import reverse_host


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
    UserCacheView,
    TemplateView
):
    template_name = 'content/index.html'
