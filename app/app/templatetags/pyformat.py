from __future__ import absolute_import, division, unicode_literals

from django import template

register = template.Library()


def pyformat(value, arg):
    return value % arg


register.filter('pyformat', pyformat)
