from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import regex
from django.utils.module_loading import import_string
from rest_framework_jsonp.renderers import JSONPRenderer

from .conf import settings

post_attachment_re = regex.compile(
    r'{media_location}/{prefix}/[\-a-z0-9]'.format(
        media_location=settings.MEDIA_LOCATION,
        prefix=settings.YAGA_ATTACHMENT_PREFIX
    ) + r'{32,36}'
)

uuid_re = '[0-9a-f]{8}-*[0-9a-f]{4}-*[0-9a-f]{4}-*[0-9a-f]{4}-*[0-9a-f]{12}'


jsonp_renderer = list(map(
    import_string, settings.REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES']
))
jsonp_renderer.append(JSONPRenderer)
