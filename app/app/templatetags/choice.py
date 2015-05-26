from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django import template

register = template.Library()


def choice(value, choice):
    return choice.value(value)


register.filter('choice', choice)
