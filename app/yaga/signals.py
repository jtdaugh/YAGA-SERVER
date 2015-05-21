from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from app.signals import ModelSignal

from . import models, receivers


class CodeSignal(
    ModelSignal
):
    model = models.Code
    receiver = receivers.CodeReceiver


class ContactSignal(
    ModelSignal
):
    model = models.Contact
    receiver = receivers.ContactReceiver


class DeviceSignal(
    ModelSignal
):
    model = models.Device
    receiver = receivers.DeviceReceiver


class MonkeyUserSignal(
    ModelSignal
):
    model = models.MonkeyUser
    receiver = receivers.MonkeyUserReceiver


class GroupSignal(
    ModelSignal
):
    model = models.Group
    receiver = receivers.GroupReceiver


class MemberSignal(
    ModelSignal
):
    model = models.Member
    receiver = receivers.MemberReceiver


class PostSignal(
    ModelSignal
):
    model = models.Post
    receiver = receivers.PostReceiver


class LikeSignal(
    ModelSignal
):
    model = models.Like
    receiver = receivers.LikeReceiver
