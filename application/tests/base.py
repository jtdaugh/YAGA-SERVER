from __future__ import absolute_import, division, unicode_literals

from sqlalchemy_utils.functions import create_database, database_exists
from flask.ext.testing import TestCase

from ..loader import create_app
from ..helpers import db
from .utils import create_json_client


app, celery = create_app()


if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
    create_database(app.config['SQLALCHEMY_DATABASE_URI'])


class BaseTestCase(TestCase):
    __json_client = None

    def setUp(self):
        db.drop_all()
        db.create_all()

    def create_app(self):
        return app

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @property
    def json_client(self):
        if self.__json_client is None:
            self.__json_client = create_json_client(self.app, self.client)

        return self.__json_client
