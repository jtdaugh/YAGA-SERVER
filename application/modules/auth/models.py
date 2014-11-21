from __future__ import absolute_import, division, unicode_literals

from flask.ext.security import UserMixin, RoleMixin

from ...helpers import db
from ...utils import now
from .mixins import BaseUser


roles_users = db.Table(
    'roles_users',
    db.Column(
        'user_id',
        db.Integer(),
        db.ForeignKey('user.id')
    ),
    db.Column(
        'role_id',
        db.Integer(),
        db.ForeignKey('role.id')
    )
)


class Role(db.Model, RoleMixin):
    id = db.Column(
        db.Integer(),
        primary_key=True
    )

    name = db.Column(
        db.String(80),
        unique=True
    )

    description = db.Column(
        db.String(255)
    )

    def __str__(self):
        return self.name


class User(db.Model, BaseUser, UserMixin):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    email = db.Column(
        db.String(255),
        unique=True
    )

    password = db.Column(
        db.String(255)
    )

    active = db.Column(
        db.Boolean(),
        default=True
    )

    created_at = db.Column(
        db.DateTime(),
        default=now
    )

    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )

    def __str__(self):
        return self.email
