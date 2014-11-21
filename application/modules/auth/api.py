from __future__ import absolute_import, division, unicode_literals

from flask import Blueprint, g
from flask.ext.security import login_user, logout_user

from ...decorators import marshal_with_form, anonymous_user_required
from ...mixins import BaseApi, BaseResource
from ...utils import b
from .forms import UserRegisterForm, UserLoginForm
from .repository import user_storage


class RegisterResource(BaseResource):
    @anonymous_user_required
    @marshal_with_form(UserRegisterForm, 400)
    def post(self):
        user = user_storage.create(
            email=self.form.email.data,
            password=self.form.password.data
        )

        login_user(user)

        return {
            'email': g.user.email
        }, 201


class LoginResource(BaseResource):
    @anonymous_user_required
    @marshal_with_form(UserLoginForm, 401)
    def post(self):
        login_user(self.form.user)

        return {
            'email': g.user.email
        }, 200


class LogoutResource(BaseResource):
    def post(self):
        if g.user.is_authenticated():
            logout_user()

        return {
        }, 200


blueprint = Blueprint('api_auth', __name__)


api = BaseApi(blueprint, prefix='/auth')
api.add_resource(RegisterResource, '/register', endpoint=b('register'))
api.add_resource(LoginResource, '/login', endpoint=b('login'))
api.add_resource(LogoutResource, '/logout', endpoint=b('logout'))
