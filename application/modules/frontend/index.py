from flask import Blueprint, render_template
from flask.views import MethodView


blueprint = Blueprint('index', __name__,)


class IndexView(MethodView):
    def get(self):
        return render_template('index.html')


blueprint.add_url_rule('/', view_func=IndexView.as_view('index'))
