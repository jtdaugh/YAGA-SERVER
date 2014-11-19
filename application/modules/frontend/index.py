from __future__ import absolute_import, division, unicode_literals

from flask import Blueprint, render_template
from flask.views import MethodView

from .tasks import test
from ...utils import b


blueprint = Blueprint('index', __name__,)


class IndexView(MethodView):
    def get(self):
        test.delay(23, 42)

        return render_template('index.html')


blueprint.add_url_rule('/', view_func=IndexView.as_view(b('index')))
