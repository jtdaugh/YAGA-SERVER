from __future__ import absolute_import, division, unicode_literals

from functools import wraps

from flask import g, abort
from flask.ext.security import logout_user


def anonymous_user_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if g.user.is_authenticated():
            abort(401)

        return fn(*args, **kwargs)
    return wrapper


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if g.user.is_authenticated():
            if not g.user.is_active():
                logout_user()
                abort(401)

            return fn(*args, **kwargs)
        else:
            abort(403)
    return wrapper


def marshal_with_form(form_obj, fail_status_code):
    def wrapped(fn):
        @wraps(fn)
        def wrapper(cls, *args, **kwargs):
            form = form_obj()

            if form.validate_on_submit():
                cls.form = form

                return fn(cls, *args, **kwargs)
            else:
                return form.errors, fail_status_code

        return wrapper

    return wrapped


def after_this_request(fn):
    @wraps(fn)
    def wrapper(response):
        if not hasattr(g, 'after_request_callbacks'):
            g.after_request_callbacks = []

        g.after_request_callbacks.append(fn)

        return fn(response)

    return wrapper
