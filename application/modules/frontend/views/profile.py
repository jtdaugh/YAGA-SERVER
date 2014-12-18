from __future__ import absolute_import, division, unicode_literals

from flask import render_template

from ....utils import b
from ....views import BaseMethodView, BaseBlueprint


blueprint = BaseBlueprint('profile', __name__)


class SummaryView(BaseMethodView):
    def get(self):
        return render_template('profile/summary.html')


blueprint.add_url_rule('/summary', view_func=SummaryView.as_view(b('summary')))
