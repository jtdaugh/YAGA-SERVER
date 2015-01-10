from __future__ import absolute_import, division, unicode_literals

from classytags.core import Options, Tag
from django import template

from ..utils import nless

register = template.Library()


class Nless(
    Tag
):
    name = 'nless'

    options = Options(
        blocks=[('endnless', 'nodelist')],
    )

    def render_tag(self, context, nodelist):
        context.push()
        content = nodelist.render(context)
        content = nless(content)
        context.pop()
        return content


register.tag(Nless)
