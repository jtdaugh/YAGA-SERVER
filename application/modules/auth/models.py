from flask.ext.security import UserMixin, RoleMixin
from flask.ext.security.utils import encrypt_password
from flask.ext.security.utils import verify_password

from application.helpers import now, db


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

    def __unicode__(self):
        return self.name


class User(db.Model, UserMixin):
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

    def set_password(self, password):
        self.password = encrypt_password(password)

    def verify_password(self, password):
        return verify_password(password, self.password)

    def __unicode__(self):
        return self.email
