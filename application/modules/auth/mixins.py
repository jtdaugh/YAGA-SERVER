from __future__ import absolute_import, division, unicode_literals

from flask.ext.security.utils import encrypt_password, verify_password


class BaseUser(object):
    def set_password(self, password):
        self.password = encrypt_password(password)

    def verify_password(self, password):
        return verify_password(password, self.password)

    @classmethod
    def add_hook(cls, hook, fn, attr=None, *args, **kwargs):
        def wrapper(self):
            res = fn(cls=self)

            if attr is not None:
                res = getattr(res, attr)

            return res

        setattr(cls, hook, wrapper)
