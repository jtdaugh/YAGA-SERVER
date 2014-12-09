from __future__ import absolute_import, division, unicode_literals

from flask.ext.security import AnonymousUser


class BaseAnonymousUser(AnonymousUser):
    def __init__(self, *args, **kwargs):
        super(BaseAnonymousUser, self).__init__(*args, **kwargs)
