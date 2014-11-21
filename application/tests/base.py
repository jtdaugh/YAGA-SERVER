from __future__ import absolute_import, division, unicode_literals

from sqlalchemy_utils.functions import (
    create_database, drop_database, database_exists
)
from flask.ext.testing import TestCase

from ..core import app
from ..helpers import db


class BaseTestCase(TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] += '_test'

        if database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
            drop_database(app.config['SQLALCHEMY_DATABASE_URI'])

        create_database(app.config['SQLALCHEMY_DATABASE_URI'])
        db.create_all()

    def create_app(self):
        app.config['TESTING'] = True

        return app

    def tearDown(self):
        drop_database(app.config['SQLALCHEMY_DATABASE_URI'])
