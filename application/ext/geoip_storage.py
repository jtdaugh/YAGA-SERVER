from __future__ import absolute_import, division, unicode_literals

from geoip2.database import Reader

from .base import BaseStorage


class Geoip(BaseStorage):
    def __init__(self, app=None,):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.reader = Reader(
            app.config['GEOIP_MMDB']
        )

    def get_country_iso_code(self, ip):
        try:
            response = self.reader.country(ip)

            iso_code = response.country.iso_code
        except:
            iso_code = None

        return iso_code
