from __future__ import absolute_import, division, unicode_literals

from app.signals import register

from .signals import PostSignal

register(PostSignal)
