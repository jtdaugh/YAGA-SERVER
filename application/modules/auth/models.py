from flask.ext.security import UserMixin, RoleMixin
from flask.ext.security.utils import encrypt_password
from flask.ext.security.utils import verify_password

from application.helpers import now, db


class Role(db.Document, RoleMixin):
    name = db.StringField(
        max_length=80,
        required=True, unique=True
    )

    description = db.StringField(
        max_length=255
    )

    def __unicode__(self):
        return self.name


class User(db.Document, UserMixin):
    email = db.StringField(
        max_length=255,
        required=True, unique=True
    )

    password = db.StringField(
        max_length=255,
        required=True,
    )

    active = db.BooleanField(
        default=True
    )

    created_at = db.DateTimeField(
        default=now
    )

    roles = db.ListField(
        db.ReferenceField(Role), default=[]
    )

    @classmethod
    def create_user(cls, email, password):
        user = cls()
        user.email = email
        user.set_password(password)
        user.save()

        return user

    def set_password(self, password):
        self.password = encrypt_password(password)

    def verify_password(self, password):
        return verify_password(password, self.password)

    def __unicode__(self):
        return self.email
