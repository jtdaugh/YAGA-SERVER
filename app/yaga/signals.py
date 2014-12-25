from __future__ import absolute_import, division, unicode_literals

from app.signals import ModelSignal
from .models import Post, Member
from .receivers import PostReceiver, MemberReceiver


class PostSignal(ModelSignal):
    model = Post
    receiver = PostReceiver


class MemberSignal(ModelSignal):
    model = Member
    receiver = MemberReceiver
