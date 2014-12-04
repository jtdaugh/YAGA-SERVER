from __future__ import absolute_import, division, unicode_literals

from flask.ext.admin import AdminIndexView, Admin

from .modules.auth.admin import (
    user_admin, role_admin, token_admin, session_admin
)
from .mixins import BaseAbstractModelView


class IndexModelView(BaseAbstractModelView, AdminIndexView):
    pass


def create_admin(app):
    admin = Admin(index_view=IndexModelView(url='/admin'))

    admin.add_view(user_admin)
    admin.add_view(role_admin)
    admin.add_view(token_admin)
    admin.add_view(session_admin)

    admin.init_app(app)
