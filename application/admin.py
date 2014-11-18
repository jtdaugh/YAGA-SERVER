from flask.ext.admin import AdminIndexView as BaseAdminIndexView, Admin

from .modules.auth.admin import user_admin, role_admin
from .mixins import BaseAdminView


class AdminIndexView(BaseAdminView, BaseAdminIndexView):
    pass


def create_admin(app):
    admin = Admin(index_view=AdminIndexView(url='/admin'))

    admin.add_view(user_admin)
    admin.add_view(role_admin)

    admin.init_app(app)
