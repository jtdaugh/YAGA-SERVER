from celery import Celery as CeleryCls

from .base import BaseStorage


class Celery(BaseStorage):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def create_celery(self, app):
        celery_obj = CeleryCls(
            app.import_name,
            broker=app.config['CELERY_BROKER_URL']
        )

        celery_obj.conf.update(app.config)

        TaskBase = celery_obj.Task

        class ContextTask(TaskBase):
            abstract = True

            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)

        celery_obj.Task = ContextTask

        return celery_obj

    def init_app(self, app):
        celery = self.create_celery(app)

        self.merge(celery)
