from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)


class ModelReceiver(
    object
):
    @staticmethod
    def pre_save(sender, **kwargs):
        pass

    @staticmethod
    def post_save(sender, **kwargs):
        pass

    @staticmethod
    def pre_delete(sender, **kwargs):
        pass

    @staticmethod
    def post_delete(sender, **kwargs):
        pass
