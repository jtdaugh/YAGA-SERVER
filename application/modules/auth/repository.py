from ...mixins import BaseRepository
from ...helpers import db
from .models import User, Role


class UserRepository(BaseRepository):
    def create(self, email, password):
        user = self.model(
            email=email
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user

    def add_role(self, user, role):
        if role not in user.roles:
            user.roles.append(role)

            db.session.add(user)
            db.session.commit()


class RoleRepository(BaseRepository):
    def create(self, name, description):
        role = self.model(
            name=name,
            description=description
        )

        db.session.add(role)
        db.session.commit()

        return role

    def get_or_create(self, name):
        role = self.get(name=name)

        if role is None:
            role = self.create(name, name)

        return role


user_storage = UserRepository(User)
role_storage = RoleRepository(Role)
