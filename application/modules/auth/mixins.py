from __future__ import absolute_import, division, unicode_literals


class BaseUser(object):
    @classmethod
    def add_hook(cls, hook, fn, attr=None, *args, **kwargs):
        def wrapper(self):
            res = fn(cls=self)

            if attr is not None:
                res = getattr(res, attr)

            return res

        setattr(cls, hook, wrapper)
