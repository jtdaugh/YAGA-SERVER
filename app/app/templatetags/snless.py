from __future__ import absolute_import, division, unicode_literals

from classytags.core import Options, Tag
from django import template

from app.utils import snless

register = template.Library()


class Snless(
    Tag
):
    name = 'snless'

    options = Options(
        blocks=[('endsnless', 'nodelist')],
    )

    def render_tag(self, context, nodelist):
        context.push()
        content = nodelist.render(context)
        content = snless(content)
        context.pop()
        return content


register.tag(Snless)
