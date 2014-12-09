from __future__ import absolute_import, division, unicode_literals

from functools import wraps

from flask import g, abort, current_app as app

from .signals import auth_ident
from .helpers import cache, rate_limit


def anonymous_user_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if g.user.is_authenticated():
            abort(401)

        return fn(*args, **kwargs)

    return wrapper


def login_required(fn=None, required_auth_ident=None):
    def wrapped(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if g.user.is_authenticated():
                if not g.user.is_active():
                    abort(401)

                if required_auth_ident is not None:
                    if g.auth_ident != required_auth_ident:
                        abort(401)

                return fn(*args, **kwargs)
            else:
                abort(403)

            return fn(*args, **kwargs)

        return wrapper

    if fn is not None:
        return wrapped(fn)

    return wrapped


def login_session_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return login_required(
            fn=fn,
            required_auth_ident='session'
        )(*args, **kwargs)

    return wrapper


def login_header_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return login_required(
            fn=fn,
            required_auth_ident='header'
        )(*args, **kwargs)

    return wrapper


def marshal_with_form(form_obj, fail_status_code):
    def wrapped(fn):
        @wraps(fn)
        def wrapper(cls, *args, **kwargs):
            form = form_obj(csrf_enabled=False)

            if form.validate_on_submit():
                cls.form = form

                return fn(cls, *args, **kwargs)
            else:
                return {
                    'errors': form.errors
                }, fail_status_code

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


def ident_marker(ident):
    def wrapped(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            res = fn(*args, **kwargs)

            if res:
                auth_ident.send(ident)

            return res
        return wrapper

    return wrapped


def view_cache(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        cached_fn = cache.cached(
            timeout=app.config['VIEW_CACHE_TIMEOUT']
        )(fn)

        return cached_fn(*args, **kwargs)
    return wrapper


def auth_rate_limit(fn):
    @wraps(fn)
    def wrapper(ident):
        rate_limit('AUTH', ident)

        return fn(ident)
    return wrapper
