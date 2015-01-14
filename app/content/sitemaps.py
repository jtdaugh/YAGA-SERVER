from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse


class IndexSitemap(
    Sitemap
):
    def items(self):
        return ['index']

    def location(self, item):
        return reverse('index')
