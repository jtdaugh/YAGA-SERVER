from __future__ import absolute_import, division, unicode_literals

from flask import Blueprint, render_template
from ...helpers import View
from ...utils import b


blueprint = Blueprint('index', __name__,)


class LoginView(View):
    def dispatch_request(self):
        return render_template('index.html')


class LogoutView(View):
    def dispatch_request(self):
        return render_template('index.html')


blueprint.add_url_rule('/login', view_func=LoginView.as_view(b('login')))
blueprint.add_url_rule('/logout', view_func=LogoutView.as_view(b('logout')))
