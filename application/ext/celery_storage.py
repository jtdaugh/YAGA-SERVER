from __future__ import absolute_import, division, unicode_literals

import logging
from itertools import ifilter, imap

import celery
from raven.handlers.logging import SentryHandler

from .base import BaseStorage


class Celery(BaseStorage):
    def __init__(self, app=None, sentry=None):
        if app is not None:
            self.init_app(app, sentry)

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

    def task_failure(
        self,
        exception, traceback, sender, task_id,
        signal, args, kwargs, einfo, *ar, **kw
    ):
        exc_info = (type(exception), exception, traceback)

        self.sentry_logger.error(
            '{name}: {exception}'.format(
                name=exception.__class__.__name__,
                exception=exception
            ),
            exc_info=exc_info,
            extra={
                'data': {
                    'task_id': task_id,
                    'sender': sender,
                    'args': args,
                    'kwargs': kwargs
                }
            }
        )

    def init_app(self, app, sentry):
        celery_obj = self.create_celery(app)

        if sentry is not None:
            self.sentry_logger = logging.getLogger(__name__)
            self.sentry_logger.addHandler(SentryHandler(sentry.client))
            self.sentry_logger.propagate = False

            celery.signals.task_failure.connect(self.task_failure, weak=False)

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
