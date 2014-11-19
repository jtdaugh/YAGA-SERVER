from __future__ import absolute_import, division, unicode_literals

from flask.ext.admin.contrib.sqla import ModelView

from ...helpers import db
from ...mixins import BaseAdminView
from .models import User, Role


class UserModelView(BaseAdminView, ModelView):
    can_create = False
    can_delete = False

    form_columns = ['email', 'active', 'roles']
    column_list = ['email', 'active', 'created_at', 'roles']

    column_filters = ['active']


class RoleModelView(BaseAdminView, ModelView):
    can_create = False
    can_delete = False

    form_columns = ['description']


user_admin = UserModelView(User, db.session)
role_admin = RoleModelView(Role, db.session)
