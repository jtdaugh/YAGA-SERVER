from __future__ import absolute_import, division, unicode_literals

from flask import Blueprint, render_template

from ...utils import b
from ...mixins import BaseMethodView
from .tasks import TestTask


blueprint = Blueprint('index', __name__,)


class IndexView(BaseMethodView):
    def get(self):
        TestTask().delay(23, 42)

        return render_template('index.html')


blueprint.add_url_rule('/', view_func=IndexView.as_view(b('index')))
