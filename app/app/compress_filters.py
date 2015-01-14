from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from compressor.filters.css_default import CssAbsoluteFilter
from compressor.utils import staticfiles


class CustomCssAbsoluteFilter(
    CssAbsoluteFilter
):
    def find(self, basename):
        if basename and staticfiles.finders:
            return staticfiles.finders.find(basename)
