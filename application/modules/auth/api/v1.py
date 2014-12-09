from __future__ import absolute_import, division, unicode_literals

from flask import g

from ....decorators import (
    marshal_with_form, anonymous_user_required, login_header_required
)
from ....views import BaseApi, BaseResource, BaseApiBlueprint
from ....utils import b
from ....helpers import SuccessResponse
from ..forms import UserRegisterForm, UserLoginForm
from ..repository import user_storage, token_storage


class RegisterResource(BaseResource):
    @anonymous_user_required
    @marshal_with_form(UserRegisterForm, 400)
    def post(self):
        user = user_storage.create(
            email=self.form.email.data,
            password=self.form.password.data
        )

        return SuccessResponse({
            'email': user.email,
            'token': user.get_auth_token(),
        }) << 201


class LoginResource(BaseResource):
    @anonymous_user_required
    @marshal_with_form(UserLoginForm, 401)
    def post(self):
        return SuccessResponse({
            'email': self.form.user.email,
            'token': self.form.user.get_auth_token(),
        }) << 200


class LogoutResource(BaseResource):
    @login_header_required
    def delete(self):
        token_storage.delete(
            token=g.token
        )

        return SuccessResponse({
            'email': g.user.email,
        }) << 200


class InfoResource(BaseResource):
    @login_header_required
    def get(self):
        return SuccessResponse({
            'email': g.user.email,
        }) << 200


blueprint = BaseApiBlueprint('api_auth', __name__)


api = BaseApi(blueprint, prefix='/auth')
api.add_resource(
    RegisterResource,
    '/register',
    endpoint=b('register')
)
api.add_resource(
    LoginResource,
    '/login',
    endpoint=b('login')
)
api.add_resource(
    LogoutResource,
    '/logout',
    endpoint=b('logout')
)
api.add_resource(
    InfoResource,
    '/info',
    endpoint=b('info')
)
