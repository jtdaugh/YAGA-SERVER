from __future__ import absolute_import, division, unicode_literals

from sqlalchemy.exc import IntegrityError

from flask import current_app as app, g

from ...repository import BaseRepository
from ...helpers import db
from ...utils import get_random_string, now
from .models import User, Role, Token, Session


class UserRepository(BaseRepository):
    def create(self, **kwargs):
        user = self.model(
            phone=kwargs['phone'],
            name=kwargs['name']
        )

        user.set_password(kwargs['password'])

        db.session.add(user)
        db.session.commit()

        return user

    def add_role(self, user, role):
        if not isinstance(role, Role):
            role = role_storage.get_or_create(name=role)

        if role not in user.roles:
            user.roles.append(role)

            db.session.commit()

    def user_session_loader(self, user_id):
        user = self.get_user(
            id=user_id
        )

        return user


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
    def load_user(self, **kwargs):
        token = self.get(
            **kwargs
        )

        if token and token.user.is_active():
            return token.user

        return None

    def user_header_loader(self, header):
        header = header.strip()

        token = self.get(
            token=header
        )

        if token and token.user.is_active():
            user = token.user

            g.token = header
        else:
            user = None

        return user

    def create(self, *args, **kwargs):
        while True:
            try:
                token = self.model(
                    token=get_random_string(app.config['AUTH_TOKEN_LENGTH']),
                    user=kwargs['cls']
                )

                db.session.add(token)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                continue

            break

        return token


class SessionRepository(BaseRepository):
    def create(self):
        while True:
            try:
                session = self.model(
                    sid=get_random_string(app.config['SESSION_SID_LENGTH'])
                )

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
        self.filter(
            sid=kwargs.pop('sid')
        ).update(
            kwargs
        )

        db.session.commit()


user_storage = UserRepository(User)
role_storage = RoleRepository(Role)
token_storage = TokenRepository(Token)
session_storage = SessionRepository(Session)

User.add_hook('get_auth_token', token_storage.create, attr='token')
