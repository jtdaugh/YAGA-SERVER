from __future__ import absolute_import, division, unicode_literals

from flask import render_template

from ....utils import b
from ....helpers import http
from ....views import BaseMethodView, BaseBlueprint
from ....decorators import login_session_required


blueprint = BaseBlueprint('profile', __name__)


class SummaryView(BaseMethodView):
    @login_session_required
    def get(self):
        return render_template('profile/summary.html'), http.OK


blueprint.add_url_rule('/summary', view_func=SummaryView.as_view(b('summary')))
