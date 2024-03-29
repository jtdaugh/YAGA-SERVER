from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from classytags.arguments import Argument
from classytags.core import Options
from classytags.helpers import InclusionTag
from django import template
from django.utils.encoding import iri_to_uri
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _

register = template.Library()


class Paginator(
    InclusionTag
):
    name = 'paginator'
    template = 'paginator.html'

    options = Options(
        Argument('page_obj'),
        Argument('slice', required=False, default=3),
    )

    def get_context(self, context, page_obj, slice):
        request = context['request']

        get = request.GET.copy()

        # if get.get('set_language'):
        #     del get['set_language']

        def render_link(page):
            get['page'] = page
            return mark_safe('?{params}'.format(
                params=iri_to_uri(get.urlencode(safe='/'))
            ))

        if get.get('page'):
            del get['page']

        range_start = page_obj.number - slice
        if range_start < 1:
            range_start = 1

        range_end = page_obj.number + slice
        if range_end > page_obj.paginator.num_pages:
            range_end = page_obj.paginator.num_pages

        page_range = range(range_start, range_end + 1)

        pages = []

        if page_obj.number == 1:
            pages.append({
                'class': 'disabled',
                'get': render_link(page_obj.number),
                'number': '{symbol} {label}'.format(
                    symbol=mark_safe('<<'),
                    label=_('First')
                )
            })
        else:
            pages.append({
                'class': '',
                'get': render_link(1),
                'number': '{symbol} {label}'.format(
                    symbol=mark_safe('<<'),
                    label=_('First')
                )
            })

        if page_obj.has_previous():
            pages.append({
                'class': '',
                'get': render_link(page_obj.previous_page_number()),
                'number': '{symbol} {label}'.format(
                    symbol=mark_safe('<'),
                    label=_('Previous')
                )
            })

        for page in page_range:
            if page == page_obj.number:
                pages.append({
                    'class': 'active',
                    'get': render_link(page),
                    'number': mark_safe(page)
                })
            else:
                pages.append({
                    'class': '',
                    'get': render_link(page),
                    'number': mark_safe(page)
                })

        if page_obj.has_next():
            pages.append({
                'class': '',
                'get': render_link(page_obj.next_page_number()),
                'number': '{symbol} {label}'.format(
                    label=_('Next'),
                    symbol=mark_safe('>')
                )
            })

        if page_obj.number == page_obj.paginator.num_pages:
            pages.append({
                'class': 'disabled',
                'get': render_link(page_obj.paginator.num_pages),
                'number': '{symbol} {label}'.format(
                    label=_('Last'),
                    symbol=mark_safe('>>')
                )
            })
        else:
            pages.append({
                'class': '',
                'get': render_link(page_obj.paginator.num_pages),
                'number': '{symbol} {label}'.format(
                    label=_('Last'),
                    symbol=mark_safe('>>')
                )
            })

        return {
            'pages': pages
        }


register.tag(Paginator)
