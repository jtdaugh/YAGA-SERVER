from flask import Blueprint, render_template
from flask.views import MethodView

from .tasks import test


blueprint = Blueprint('index', __name__,)


class IndexView(MethodView):
    def get(self):
        test.delay(23, 42)
        return render_template('index.html')


blueprint.add_url_rule('/', view_func=IndexView.as_view('index'))
