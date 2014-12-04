from __future__ import absolute_import, division, unicode_literals

from flask_sslify import SSLify, YEAR_IN_SECS


class BaseSSLify(SSLify):
    def __init__(self, app=None, *args, **kwargs):
        super(BaseSSLify, self).__init__(app, *args, **kwargs)

    def init_app(
        self, app,
        age=YEAR_IN_SECS, subdomains=False, permanent=False
    ):
        self.app = app
        self.hsts_age = age
        self.hsts_include_subdomains = subdomains,
        self.permanent = permanent

        super(BaseSSLify, self).init_app(app)
