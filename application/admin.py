from __future__ import absolute_import, division, unicode_literals

from flask import g
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import AdminIndexView, Admin


class BaseAbstractModelView(object):
    def is_accessible(self):
        return (
            g.user.is_authenticated()
            and
            g.user.is_active()
            and
            g.user.has_role('superuser')
        )


class BaseSqlModelView(ModelView):
    @classmethod
    def as_view(cls, storage):
        return cls(*storage.admin_options)


class BaseModelView(BaseAbstractModelView, BaseSqlModelView):
    pass


class IndexModelView(BaseAbstractModelView, AdminIndexView):
    pass


def create_admin(app):
    admin = Admin(index_view=IndexModelView(url='/admin'))

    from .modules.auth.admin import (
        user_admin, role_admin, token_admin, session_admin
    )

    admin.add_view(user_admin)
    admin.add_view(role_admin)
    admin.add_view(token_admin)
    admin.add_view(session_admin)

    admin.init_app(app)
