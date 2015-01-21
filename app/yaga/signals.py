from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from app.signals import ModelSignal

from .models import Like, Member, Post
from .receivers import LikeReceiver, MemberReceiver, PostReceiver


class PostSignal(
    ModelSignal
):
    model = Post
    receiver = PostReceiver


class MemberSignal(
    ModelSignal
):
    model = Member
    receiver = MemberReceiver


class LikeSignal(
    ModelSignal
):
    model = Like
    receiver = LikeReceiver
