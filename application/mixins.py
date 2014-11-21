from __future__ import absolute_import, division, unicode_literals

from flask import g
from flask.views import View, MethodView
from flask_wtf import Form
from flask.ext.restful import Api, Resource
from flask.ext.restful import DEFAULT_REPRESENTATIONS
from flask.ext.admin.contrib.sqla import ModelView
from wtforms.validators import ValidationError

from .helpers import db, output_json


DEFAULT_REPRESENTATIONS['application/json'] = output_json


class BaseView(View):
    pass


class BaseMethodView(MethodView):
    pass


class BaseApi(Api):
    def error_router(self, original_handler, e):
        return original_handler(e)


class BaseResource(Resource):
    pass


class BaseForm(Form):
    pass


class BaseValidator(object):
    def __init__(self, message=None):
        if message is None:
            message = self.MESSAGE

        self.message = message

    @property
    def fail(self):
        return ValidationError(self.message)

    def __call__(self, form, field):
        raise NotImplemented


class BaseAbstractRepository(object):
    def __init__(self, model):
        self.model = model


class BaseSqlRepository(object):
    @property
    def admin_options(self):
        return [self.model, db.session]

    def get(self, **kwargs):
        return db.session.query(self.model).filter_by(**kwargs).first()

    def filter(self, **kwargs):
        return db.session.query(self.model).filter_by(**kwargs)

    def count(self, **kwargs):
        return self.filter(**kwargs).count()


class BaseRepository(BaseAbstractRepository, BaseSqlRepository):
    pass


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
