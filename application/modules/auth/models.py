from __future__ import absolute_import, division, unicode_literals

from flask.ext.security import UserMixin, RoleMixin

from ...helpers import db
from ...utils import now
from ...models import ModelMixin
from .mixins import BaseUser


roles_users = db.Table(
    'roles_users',
    db.Column(
        'user_id',
        db.Integer,
        db.ForeignKey('user.id')
    ),
    db.Column(
        'role_id',
        db.Integer,
        db.ForeignKey('role.id')
    )
)


class Role(db.Model, RoleMixin):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(255),
        unique=True, nullable=False
    )

    description = db.Column(
        db.String(255)
    )

    def __str__(self):
        return self.name


class User(db.Model, BaseUser, UserMixin, ModelMixin):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    phone = db.Column(
        db.String(255),
        unique=True, nullable=False
    )

    name = db.Column(
        db.String(255),
        unique=True, nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    active = db.Column(
        db.Boolean(),
        nullable=False,
        default=True
    )

    created_at = db.Column(
        db.DateTime(),
        nullable=False,
        default=now
    )

    verified = db.Column(
        db.Boolean(),
        nullable=False,
        default=False
    )

    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )

    tokens = db.relationship(
        'Token',
        backref='user',
        lazy='dynamic'
    )

    sessions = db.relationship(
        'Session',
        backref='user',
        lazy='dynamic'
    )

    def get_auth_token(self):
        raise NotImplementedError

    def __str__(self):
        return self.name


class Token(db.Model):
    token = db.Column(
        db.String(255),
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(),
        nullable=False,
        default=now
    )

    def __str__(self):
        return self.token


class Session(db.Model):
    sid = db.Column(
        db.String(256),
        primary_key=True
    )

    data = db.Column(
        db.Text(),
        nullable=False,
        default='{}'
    )

    expire_at = db.Column(
        db.DateTime(),
        nullable=False,
        default=now
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=True
    )

    def __str__(self):
        return self.sid
