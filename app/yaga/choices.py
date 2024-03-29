from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from app.utils import Choice


class VendorChoice(
    Choice
):
    IOS = 0
    ANDROID = 1


class StateChoice(
    Choice
):
    PENDING = 0
    UPLOADED = 1
    READY = 5
    DELETED = 10


class StatusChoice(
    Choice
):
    MEMBER = 0
    FOLLOWER = 1
    LEFT = 5
    PENDING = 10


class ApprovalChoice(
    Choice
):
    WAITING = 0
    APPROVED = 1
    REJECTED = 5
