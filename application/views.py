from __future__ import absolute_import, division, unicode_literals

from flask.views import View, MethodView
from flask import Blueprint
from flask.ext.restful import Api, Resource
from flask.ext.restful import DEFAULT_REPRESENTATIONS

from .helpers import output_json, csrf


DEFAULT_REPRESENTATIONS['application/json'] = output_json


class BaseView(View):
    pass


class BaseMethodView(MethodView):
    pass


class BaseApi(Api):
    def error_router(self, original_handler, e):
        return original_handler(e)


class BaseResource(Resource):
    pass


class BaseBlueprint(Blueprint):
    pass


class BaseApiBlueprint(BaseBlueprint):
    def __init__(self, *args, **kwargs):
        super(BaseApiBlueprint, self).__init__(*args, **kwargs)

        csrf.exempt(self)
