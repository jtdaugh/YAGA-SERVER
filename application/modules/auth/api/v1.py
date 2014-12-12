from __future__ import absolute_import, division, unicode_literals

from flask import g

from ....decorators import (
    marshal_with_form, anonymous_user_required, login_header_required
)
from ....views import BaseApi, BaseResource, BaseApiBlueprint
from ....utils import b
from ....helpers import SuccessResponse
from ..forms import UserRegisterForm, UserLoginForm, UserLogoutForm
from ..repository import user_storage, token_storage


class RegisterResource(BaseResource):
    @anonymous_user_required
    @marshal_with_form(UserRegisterForm, 400)
    def post(self):
        user = user_storage.create(
            name=self.form.name.data,
            phone=self.form.phone.data,
            password=self.form.password.data
        )

        return SuccessResponse({
            'token': user.get_auth_token(),
        }) << 201


class LoginResource(BaseResource):
    @anonymous_user_required
    @marshal_with_form(UserLoginForm, 401)
    def post(self):
        return SuccessResponse({
            'token': self.form.obj.get_auth_token(),
        }) << 200


class LogoutResource(BaseResource):
    @login_header_required
    @marshal_with_form(UserLogoutForm, 401)
    def post(self):
        token_storage.delete(
            token=g.token
        )

        return SuccessResponse({
            'token': g.token
        }) << 200


class InfoResource(BaseResource):
    @login_header_required
    def get(self):
        return SuccessResponse({
            'name': g.user.name,
            'phone': g.user.phone
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
