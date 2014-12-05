from sqlalchemy.orm import class_mapper

from .helpers import db


class ModelMixin(object):
    @property
    def pk(self):
        pk_attr = class_mapper(self.__class__).primary_key[0].name
        pk = getattr(self, pk_attr)

        return pk

    def save(self):
        if not self.pk:
            db.session.add(self)

        db.session.commit()
