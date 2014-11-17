from flask import Blueprint
from flask.ext.security import login_user, logout_user

from application.helpers import (
    Api, Resource, marshal_with_form, anonymous_user_required, login_required
)
from .forms import UserRegisterForm, UserLoginForm
from .models import User


class RegisterResource(Resource):
    @anonymous_user_required
    @marshal_with_form(UserRegisterForm)
    def post(self):
        user = User.create_user(
            email=self.form.email.data,
            password=self.form.password.data
        )

        return {
            'email': user.email
        }


class LoginResource(Resource):
    @anonymous_user_required
    @marshal_with_form(UserLoginForm)
    def post(self):
        login_user(self.form.user)

        return {
            'email': self.form.user.email
        }


class LogoutResource(Resource):
    @login_required
    def post(self):
        logout_user()

        return {
            'status': 'done'
        }

    def get(self):
        return self.post()


blueprint = Blueprint('api_auth', __name__)


api = Api(blueprint, prefix='/auth')
api.add_resource(RegisterResource, '/register', endpoint='register')
api.add_resource(LoginResource, '/login', endpoint='login')
api.add_resource(LogoutResource, '/logout', endpoint='logout')
