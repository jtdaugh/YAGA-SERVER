from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from app.signals import ModelSignal

from .models import Post
from .receivers import PostReceiver


class PostSignal(
    ModelSignal
):
    model = Post
    receiver = PostReceiver
