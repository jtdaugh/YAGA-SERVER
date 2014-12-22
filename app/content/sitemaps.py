from __future__ import absolute_import, division, unicode_literals

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse


class IndexSitemap(
    Sitemap
):
    def items(self):
        return ['index']

    def location(self, item):
        return reverse('index')
