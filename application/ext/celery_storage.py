from __future__ import absolute_import, division, unicode_literals

from itertools import ifilter, imap

import celery

from .base import BaseStorage


class Celery(BaseStorage):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def create_celery(self, app):
        celery_obj = celery.Celery(
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

        PeriodicTaskBase = celery.task.PeriodicTask

        class ContextPeriodicTask(PeriodicTaskBase):
            abstract = True

            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return PeriodicTaskBase.__call__(self, *args, **kwargs)

        celery_obj.PeriodicTask = ContextPeriodicTask

        return celery_obj

    def init_app(self, app):
        celery_obj = self.create_celery(app)

        self.merge(celery_obj)

    def autodiscover(self, packages):
        def is_module(module):
            if '__' in module:
                return False

            for skip in [
                'absolute_import', 'division', 'unicode_literals'
            ]:
                if skip in module:
                    return False

            return True

        modules = imap(
            lambda module: packages.__name__ + '.' + module, dir(packages)
        )

        modules = list(ifilter(is_module, list(modules)))

        self.autodiscover_tasks(modules)
