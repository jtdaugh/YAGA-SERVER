from __future__ import absolute_import, division, unicode_literals

from app.signals import ModelSignal
from .models import Post
from .receivers import PostReceiver


class PostSignal(ModelSignal):
    model = Post
    receiver = PostReceiver
