from __future__ import absolute_import, division, unicode_literals

from flask import g, current_app as app

from .....decorators import (
    marshal_with_form, anonymous_user_required, login_header_required
)
from .....views import BaseApi, BaseResource, BaseApiBlueprint
from .....utils import b, now
from .....helpers import SuccessResponse, FailResponse, phone
from .forms import (
    UserRegisterApiForm, UserLoginApiForm, UserLogoutApiForm,
    CodeRequestApiForm, PhoneApiForm
)
from ...repository import user_storage, token_storage, code_storage


class RegisterResource(BaseResource):
    @anonymous_user_required
    @marshal_with_form(UserRegisterApiForm, 422)
    def post(self):
        user = user_storage.create(
            name=self.form.name.data,
            phone=self.form.phone.data,
        )

        return SuccessResponse({
            'token': user.get_auth_token(),
        }) << 201


class CodeRequestResource(BaseResource):
    @anonymous_user_required
    @marshal_with_form(CodeRequestApiForm, 422)
    def post(self):
        request_id = phone.send_verify(
            self.form.phone.data,
            locale=g.locale
        )

        if not request_id:
            return FailResponse({
                'phone': ['transport_error'],
            }) << 200

        code = code_storage.create(
            request_id=request_id,
            phone=self.form.phone.data,
            expire_at=now() + app.config['SMS_VERIFICATION_DELTA']
        )

        if code is None:
            return FailResponse({
                'phone': ['storage_error'],
            }) << 200

        return SuccessResponse({
            'phone': self.form.phone.data,
        }) << 200


class LoginResource(BaseResource):
    @anonymous_user_required
    @marshal_with_form(UserLoginApiForm, 422)
    def post(self):
        return SuccessResponse({
            'token': self.form.obj.get_auth_token(),
        }) << 200


class LogoutResource(BaseResource):
    @login_header_required
    @marshal_with_form(UserLogoutApiForm, 401)
    def post(self):
        token_storage.delete(
            token=g.token
        )

        return SuccessResponse({
            'token': None
        }) << 200


class AboutResource(BaseResource):
    @login_header_required
    def get(self):
        return SuccessResponse({
            'name': g.user.name,
            'phone': g.user.phone
        }) << 200


class InfoResource(BaseResource):
    @anonymous_user_required
    @marshal_with_form(PhoneApiForm, 422)
    def post(self):
        is_user = user_storage.get(
            phone=self.form.phone.data
        )

        return SuccessResponse({
            'user': bool(is_user)
        }) << 200


blueprint = BaseApiBlueprint('api_auth', __name__)


api = BaseApi(blueprint, prefix='/auth')
api.add_resource(
    CodeRequestResource,
    '/request',
    endpoint=b('request')
)
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
    AboutResource,
    '/about',
    endpoint=b('about')
)
api.add_resource(
    InfoResource,
    '/info',
    endpoint=b('info')
)
