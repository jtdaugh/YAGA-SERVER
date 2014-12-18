from __future__ import absolute_import, division, unicode_literals

from sqlalchemy.exc import IntegrityError

from flask import request, current_app as app, g

from ...repository import BaseRepository
from ...helpers import db
from ...utils import get_random_string, now, encrypt, decrypt
from .models import User, Role, Token, Session, Code


class UserRepository(BaseRepository):
    def add_role(self, user, role):
        if not isinstance(role, Role):
            role = role_storage.get_or_create(name=role)

        if role not in user.roles:
            user.roles.append(role)

            db.session.commit()


class RoleRepository(BaseRepository):
    def get_or_create(self, **kwargs):
        role = self.get(
            name=kwargs['name']
        )

        if not kwargs.get('description'):
            kwargs['description'] = kwargs['name']

        if role is None:
            role = self.create(
                **kwargs
            )

        return role


class TokenRepository(BaseRepository):
    def user_header_loader(self, header):
        header = header.strip()

        if app.config['CRYPT_SID']:
            try:
                header = decrypt(header)
            except Exception:
                return None

        token = self.get(
            token=header
        )

        if token:
            self.update_usage(token)

            if token.user.is_active():
                user = token.user

                g.token = token.token
            else:
                user = None
        else:
            user = None

        return user

    def get_auth_token(self, **kwargs):
        user = kwargs['cls']

        token = self.create(user=user)

        if app.config['CRYPT_SID']:
            token = encrypt(token.token)
        else:
            token = token.token

        return token

    def create(self, *args, **kwargs):
        while True:
            try:
                token = self.model(
                    token=get_random_string(app.config['AUTH_TOKEN_LENGTH']),
                    user=kwargs['user']
                )

                self.update_usage(token)
                db.session.add(token)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                continue

            break

        return token

    def update_usage(self, token):
        token.last_ip = request.remote_addr
        token.last_usage = now()


class SessionRepository(BaseRepository):
    def create(self):
        while True:
            try:
                session = self.model(
                    sid=get_random_string(app.config['SESSION_SID_LENGTH'])
                )

                self.update_usage(session)
                db.session.add(session)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                continue

            break

        return session

    def get_not_expired(self, **kwargs):
        query = [self.model.expire_at > now()]

        for key, value in kwargs.items():
            query.append(
                getattr(self.model, key) == value
            )

        return db.session.query(self.model).filter(
            *query
        ).first()

    def filter_expired(self, **kwargs):
        query = [self.model.expire_at <= now()]

        for key, value in kwargs.items():
            query.append(
                getattr(self.model, key) == value
            )

        return db.session.query(self.model).filter(
            *query
        )

    def delete_expired(self):
        result = self.filter_expired().delete()

        db.session.commit()

        return result

    def update(self, **kwargs):
        sid = kwargs.pop('sid')

        self.update_usage(kwargs)

        self.filter(
            sid=sid
        ).update(
            kwargs
        )

        db.session.commit()

    def update_usage(self, session):
        if isinstance(session, dict):
            session['last_ip'] = request.remote_addr
            session['last_usage'] = now()
        else:
            setattr(session, 'last_ip', request.remote_addr)
            setattr(session, 'last_usage', now())


class CodeRepository(BaseRepository):
    def get_latest_request(self, phone):
        code = db.session.query(self.model).filter_by(
            phone=phone
        ).order_by(self.model.expire_at.desc()).first()

        return code

    def filter_expired(self, **kwargs):
        query = [self.model.expire_at <= now()]

        for key, value in kwargs.items():
            query.append(
                getattr(self.model, key) == value
            )

        return db.session.query(self.model).filter(
            *query
        )

    def delete_expired(self):
        result = self.filter_expired().delete()

        db.session.commit()

        return result

    def mark_as_validated(self, code):
        code.validated = True

        db.session.commit()


user_storage = UserRepository(User)
role_storage = RoleRepository(Role)
token_storage = TokenRepository(Token)
session_storage = SessionRepository(Session)
code_storage = CodeRepository(Code)


User.add_hook('get_auth_token', token_storage.get_auth_token)
