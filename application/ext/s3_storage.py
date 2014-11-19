from boto.s3.connection import S3Connection


class S3(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.connection = S3Connection(
            app.config['AWS_ACCESS_KEY_ID'],
            app.config['AWS_SECRET_ACCESS_KEY']
        )

        self.bucket = self.connection.get_bucket(
            app.config['S3_BUCKET_NAME_MEDIA']
        )
