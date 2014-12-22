from __future__ import absolute_import, division, unicode_literals

from django import template
from classytags.core import Tag, Options

from app.utils import nless


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
