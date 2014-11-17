from collections import MutableMapping

from flask import g
from flask.views import View as BaseView
from flask_wtf import Form as BaseForm
from flask.ext.restful import Api as BaseApi, Resource as BaseResource
from flask.ext.restful import DEFAULT_REPRESENTATIONS
from wtforms.validators import ValidationError

from .helpers import output_json


DEFAULT_REPRESENTATIONS['application/json'] = output_json


class View(BaseView):
    pass


class Api(BaseApi):
    def error_router(self, original_handler, e):
        return original_handler(e)


class Resource(BaseResource):
    pass


class Form(BaseForm):
    pass


class Validator(object):
    def __init__(self, message=None):
        if message is None:
            message = self.MESSAGE

        self.message = message

    @property
    def fail(self):
        return ValidationError(self.message)

    def __call__(self, form, field):
        pass


class BaseAdminView(object):
    def is_accessible(self):
        return (
            g.user.is_authenticated()
            and
            g.user.is_active()
            and
            g.user.has_role('superuser')
        )


class DummyDict(MutableMapping):
    @property
    def dct(self):
        return self.__dict__

    def __getitem__(self, key):
        try:
            return self.dct[key]
        except:
            return None

    def __setitem__(self, key, value):
        self.dct[key] = value

        return self[key]

    def __delitem__(self, key):
        try:
            del self.dct[key]
        except KeyError:
            pass

    def __iter__(self):
        return self.dct.__iter__()

    def __len__(self):
        return self.dct.__len__()
