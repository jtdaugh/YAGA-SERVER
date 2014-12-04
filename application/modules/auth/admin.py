from __future__ import absolute_import, division, unicode_literals

from ...mixins import BaseModelView
from .repository import (
    user_storage, role_storage, token_storage, session_storage
)


class UserModelView(BaseModelView):
    can_create = False
    can_delete = False
    can_edit = True

    form_columns = ['active', 'roles']
    column_list = ['email', 'active', 'created_at', 'roles']

    column_filters = ['active']


class RoleModelView(BaseModelView):
    can_create = False
    can_delete = False
    can_edit = True

    form_columns = ['users', 'description']
    column_list = ['name', 'description']


class TokenModelView(BaseModelView):
    can_create = False
    can_delete = True
    can_edit = True

    column_list = ['user']
    form_columns = ['user', 'token']


class SessionModelView(BaseModelView):
    can_create = False
    can_delete = True
    can_edit = True

    form_columns = ['user', 'sid']
    column_list = ['user', 'expire_at']


user_admin = UserModelView.as_view(user_storage)
role_admin = RoleModelView.as_view(role_storage)
token_admin = TokenModelView.as_view(token_storage)
session_admin = SessionModelView.as_view(session_storage)
