from __future__ import absolute_import, division, unicode_literals

from ...helpers import celery


@celery.task
def test(a, b):
    return a + b
