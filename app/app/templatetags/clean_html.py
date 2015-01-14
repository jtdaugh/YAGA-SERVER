from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import nltk
from django import template
from django.utils.safestring import mark_safe

from ..utils import snless

register = template.Library()


def clean_html(html):
    return mark_safe(snless(nltk.clean_html(html)))


register.filter('clean_html', clean_html)
