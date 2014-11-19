from application.helpers import celery


@celery.task
def test(a, b):
    return a + b
