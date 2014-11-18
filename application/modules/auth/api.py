from flask import Blueprint, g, current_app as app
from flask.ext.security import login_user, logout_user

from application.helpers import (
    db, marshal_with_form, anonymous_user_required, login_required
)
from application.mixins import Api, Resource
from .forms import UserRegisterForm, UserLoginForm


class RegisterResource(Resource):
    @anonymous_user_required
    @marshal_with_form(UserRegisterForm)
    def post(self):
        user = app.user_datastore.create_user(
            email=self.form.email.data
        )
        user.set_password(self.form.password.data)

        db.session.commit()

        login_user(user)

        return {
            'email': g.user.email
        }


class LoginResource(Resource):
    @anonymous_user_required
    @marshal_with_form(UserLoginForm)
    def post(self):
        login_user(self.form.user)

        return {
            'email': g.user.email
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
