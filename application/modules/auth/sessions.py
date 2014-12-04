from __future__ import absolute_import, division, unicode_literals

from flask import json, g
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin

from ...utils import now
from .repository import session_storage


class SqlSession(CallbackDict, SessionMixin):
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


class SqlSessionInterface(SessionInterface):
    def __init__(self):
        self.storage = session_storage
        self.session_class = SqlSession
        self.serializer = json

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)

        if not sid:
            return self.session_class()

        session = self.storage.get_not_expired(
            sid=sid,
        )

        if session:
            data = self.serializer.loads(session.data)

            return self.session_class(data, sid=sid)
        else:
            return self.session_class()

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)

        if not session:
            if session.sid:
                self.storage.delete(sid=session.sid)

            if session.modified:
                response.delete_cookie(
                    app.session_cookie_name,
                    domain=domain
                )

            return

        data = self.serializer.dumps(dict(session))

        if not session.sid:
            session.sid = self.storage.create().sid

        try:
            if g.user.is_authenticated():
                user_id = g.user.id
            else:
                raise AttributeError
        except AttributeError:
            user_id = None

        self.storage.update(
            sid=session.sid,
            expire_at=now() + app.permanent_session_lifetime,
            data=data,
            user_id=user_id
        )

        response.set_cookie(
            app.session_cookie_name,
            session.sid,
            expires=self.get_expiration_time(app, session),
            httponly=True,
            domain=domain
        )
