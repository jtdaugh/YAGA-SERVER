from __future__ import absolute_import, division, unicode_literals


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
