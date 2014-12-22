from __future__ import absolute_import, division, unicode_literals

from compressor.filters.css_default import CssAbsoluteFilter
from compressor.utils import staticfiles


class CustomCssAbsoluteFilter(
    CssAbsoluteFilter
):
    def find(self, basename):
        if basename and staticfiles.finders:
            return staticfiles.finders.find(basename)
