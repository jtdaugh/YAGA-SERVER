from .local import Config as BaseConfig


class Config(BaseConfig):
    TESTING = True

    SQLALCHEMY_DATABASE_URI = 'postgresql://hell:@127.0.0.1:5432/yaga_test'
