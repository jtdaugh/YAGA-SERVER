from .local import Config as BaseConfig


class Config(BaseConfig):
    DEBUG = True

    TESTING = True

    SQLALCHEMY_DATABASE_URI = 'postgresql://:@127.0.0.1:5432/yaga_test'
