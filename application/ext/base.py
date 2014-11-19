from __future__ import absolute_import, division, unicode_literals


class BaseStorage(object):
    def merge(self, obj):
        for key in dir(obj):
            if not hasattr(self, key):
                setattr(self, key, getattr(obj, key))
