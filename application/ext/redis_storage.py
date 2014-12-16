from __future__ import absolute_import, division, unicode_literals

from flask import json, current_app as app
from redis import StrictRedis
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin

from ..utils import get_random_string, encrypt, decrypt
from .base import BaseStorage


class RedisSession(CallbackDict, SessionMixin):
    @property
    def permanent(self):
        return True

    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class RedisSessionInterface(SessionInterface):
    @property
    def sid_length(self):
        return app.config['SESSION_SID_LENGTH']

    def __init__(self, redis, prefix=None):
        if prefix is None:
            prefix = 'session'

        self.redis = redis
        self.prefix = prefix
        self.session_class = RedisSession
        self.serializer = json

    def key(self, suffix):
        return '{prefix}:{suffix}'.format(
            prefix=self.prefix,
            suffix=suffix
        )

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)

        if not sid:
            return self.session_class()

        if app.config['CRYPT_SID']:
            sid = decrypt(sid)

            if not sid:
                return self.session_class()

        data = self.redis.get(self.key(sid))

        if data:
            data = self.serializer.loads(data)

            return self.session_class(data, sid=sid)
        else:
            return self.session_class()

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)

        if not session:
            if session.sid:
                self.redis.delete(self.key(session.sid))

            if session.modified:
                response.delete_cookie(
                    app.session_cookie_name,
                    domain=domain
                )

            return

        data = self.serializer.dumps(dict(session))

        if not session.sid:
            while True:
                sid = get_random_string(self.sid_length)

                if self.redis.setnx(
                    self.key(sid),
                    data
                ):
                    break

            session.sid = sid

            self.redis.expire(
                self.key(sid),
                int(app.permanent_session_lifetime.total_seconds())
            )
        else:
            self.redis.setex(
                self.key(session.sid),
                int(app.permanent_session_lifetime.total_seconds()),
                data
            )

        sid = session.sid

        if app.config['CRYPT_SID']:
            sid = encrypt(session.sid)

        response.set_cookie(
            app.session_cookie_name,
            sid,
            expires=self.get_expiration_time(app, session),
            httponly=True,
            domain=domain
        )


class Redis(BaseStorage):
    def __init__(self, app=None,):
        self.prefix = 'REDIS'

        if app is not None:
            self.init_app(app)

    def key(self, suffix):
        return '{prefix}_{suffix}'.format(
            prefix=self.prefix,
            suffix=suffix
        )

    def config(self, option, fallback):
        return self.app.config.get(self.key(option), fallback)

    def init_app(self, app):
        self.app = app

        redis = StrictRedis(
            host=self.config('HOST', '127.0.0.1'),
            port=self.config('PORT', 6379),
            password=self.config('PASSWORD', None),
            db=self.config('DB', 0),
        )

        self.merge(redis)
