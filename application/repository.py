from __future__ import absolute_import, division, unicode_literals

from .helpers import db


class BaseAbstractRepository(object):
    def __init__(self, model):
        self.model = model


class BaseSqlRepository(object):
    @property
    def admin_options(self):
        return [self.model, db.session]

    def delete(self, **kwargs):
        result = db.session.query(self.model).filter_by(**kwargs).delete()
        db.session.commit()

        return result

    def get(self, **kwargs):
        return self.filter(**kwargs).first()

    def filter(self, **kwargs):
        return db.session.query(self.model).filter_by(**kwargs)

    def count(self, **kwargs):
        return self.filter(**kwargs).count()

    def update(self, *args, **kwargs):
        raise NotImplementedError

    def update_obj(self, obj, *args, **kwargs):
        raise NotImplementedError

    def create(self, **kwargs):
        obj = self.model(**kwargs)

        db.session.add(obj)
        db.session.commit()

        return obj


class BaseRepository(BaseAbstractRepository, BaseSqlRepository):
    pass
