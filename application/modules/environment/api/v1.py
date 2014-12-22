from __future__ import absolute_import, division, unicode_literals

from flask import request

from ....views import BaseApi, BaseResource, BaseApiBlueprint
from ....utils import b, phone_tools
from ....helpers import geoip, SuccessResponse, http


class CodesResource(BaseResource):
    def get(self):
        iso_code = geoip.get_country_iso_code(request.remote_addr)

        codes = phone_tools.get_country_codes()

        propose = iso_code if iso_code in codes else None

        return SuccessResponse({
            'codes': codes,
            'propose': propose
        }), http.OK


blueprint = BaseApiBlueprint('environment', __name__)


api = BaseApi(blueprint, prefix='/environment')
api.add_resource(
    CodesResource,
    '/codes',
    endpoint=b('codes')
)
