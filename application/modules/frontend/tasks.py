from __future__ import absolute_import, division, unicode_literals

from ...helpers import celery


class TestTask(celery.Task):
    def run(self, a, b):
        return a + b
