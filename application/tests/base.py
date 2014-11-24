from __future__ import absolute_import, division, unicode_literals

from sqlalchemy_utils.functions import create_database, database_exists
from flask.ext.testing import TestCase

from ..loader import create_app
from ..helpers import db


app, celery = create_app()


if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
    create_database(app.config['SQLALCHEMY_DATABASE_URI'])


class BaseTestCase(TestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()

    def create_app(self):
        return app

    def tearDown(self):
        db.drop_all()
