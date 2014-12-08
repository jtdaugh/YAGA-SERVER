from __future__ import absolute_import, division, unicode_literals

from phonenumbers import COUNTRY_CODE_TO_REGION_CODE


class PhoneRepository(object):
    def get_codes(self):
        _map = {}

        for code, countries in COUNTRY_CODE_TO_REGION_CODE.items():
            for country in countries:
                if country != '001' and country not in _map:
                    _map[country] = '+{code}'.format(
                        code=code
                    )

        return _map


phone_storage = PhoneRepository()
