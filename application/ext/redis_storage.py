from __future__ import absolute_import, division, unicode_literals

from flask.json import dumps, loads
from redis import StrictRedis
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin

from ..utils import get_random_string
from .base import BaseStorage


class JsonSerializer(object):
    def dumps(self, data):
        return dumps(data)

    def loads(self, data):
        return loads(data)


json_serializer = JsonSerializer()


class RedisSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.permanent = True
        self.modified = False


class RedisSessionInterface(SessionInterface):
    RANDOM_STRING_LENGTH = 32

    def __init__(self, redis, prefix=None):
        if prefix is None:
            prefix = 'session'

        self.redis = redis
        self.prefix = prefix
        self.session_class = RedisSession
        self.serializer = json_serializer

    def key(self, suffix):
        return '{prefix}:{suffix}'.format(
            prefix=self.prefix,
            suffix=suffix
        )

    def new_session(self):
        while True:
            sid = get_random_string(self.RANDOM_STRING_LENGTH)

            if self.redis.setnx(self.key(sid), '{}'):
                break

        return self.session_class(sid=sid, new=True)

    def ttl(self, app):
        return int(app.permanent_session_lifetime.total_seconds())

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)

        if not sid:
            return self.new_session()

        data = self.redis.get(self.key(sid))

        if data:
            data = self.serializer.loads(data)

            return self.session_class(data, sid=sid)
        else:
            return self.new_session()

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)

        if not session:
            self.redis.delete(self.key(session.sid))

            if session.modified:
                response.delete_cookie(
                    app.session_cookie_name,
                    domain=domain
                )

            return

        cookie_ttl = self.get_expiration_time(app, session)

        data = self.serializer.dumps(dict(session))

        self.redis.setex(
            self.key(session.sid),
            self.ttl(app),
            data
        )

        response.set_cookie(
            app.session_cookie_name,
            session.sid,
            expires=cookie_ttl,
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
