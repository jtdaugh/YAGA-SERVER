from flask import Blueprint, render_template
from flask.views import View


blueprint = Blueprint('index', __name__,)


class LoginView(View):
    def dispatch_request(self):
        return render_template('index.html')


blueprint.add_url_rule('/login', view_func=IndexView.as_view('login'))
blueprint.add_url_rule('/logout', view_func=IndexView.as_view('logout'))
