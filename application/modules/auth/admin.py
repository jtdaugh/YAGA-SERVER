from __future__ import absolute_import, division, unicode_literals

from ...mixins import BaseModelView
from .repository import user_storage, role_storage


class UserModelView(BaseModelView):
    can_create = False
    can_delete = False

    form_columns = ['active', 'roles']
    column_list = ['email', 'active', 'created_at', 'roles']

    column_filters = ['active']


class RoleModelView(BaseModelView):
    can_create = False
    can_delete = False

    form_columns = ['users']
    column_list = ['name', 'description']


user_admin = UserModelView.as_view(user_storage)
role_admin = RoleModelView.as_view(role_storage)
