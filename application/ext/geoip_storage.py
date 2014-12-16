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
        return self.get_geo_data(ip)['iso_code']

    def get_geo_data(self, ip):
        data = {
            'city': None,
            'country': None,
            'iso_code': None
        }

        try:
            response = self.reader.city(ip)

            if response.city.name:
                data['city'] = response.city.name

            if response.country.name:
                data['country'] = response.country.name

            if response.country.iso_code:
                data['iso_code'] = response.country.iso_code

        except:
            pass

        return data
