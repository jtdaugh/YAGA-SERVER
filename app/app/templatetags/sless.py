from __future__ import absolute_import, division, unicode_literals

from classytags.core import Options, Tag
from django import template

from ..utils import sless

register = template.Library()


class Sless(
    Tag
):
    name = 'sless'

    options = Options(
        blocks=[('endsless', 'nodelist')],
    )

    def render_tag(self, context, nodelist):
        context.push()
        content = nodelist.render(context)
        content = sless(content)
        context.pop()
        return content


register.tag(Sless)
