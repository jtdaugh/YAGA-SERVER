from __future__ import (
    absolute_import, division, unicode_literals, print_function
)

from time import sleep

from fabric.api import local, task, warn_only
from fabric.operations import prompt


PROCESS_WORKERS = 2
DYNOS = {
    'web': 1,
    'celery_broker': 1,
    'celery_worker': 0,
}
USE_NEWRELIC = True
STOP_TIMEOUT = 30
START_TIMEOUT = 30

NEWRELIC_CMD = 'newrelic-admin run-program '


def ensure_prompt(label):
    value = None
    label = '{label}: '.format(
        label=label
    )

    while not value:
        value = prompt(label)

    return value.strip()


@task
def uwsgi():
    cmd = 'uwsgi --http-keepalive=0 --module=application.core:app --master --processes={workers} --harakiri=30 --vacuum --single-interpreter --enable-threads --http :$PORT'

    cmd = cmd.format(
        workers=PROCESS_WORKERS
    )

    if USE_NEWRELIC:
        cmd = NEWRELIC_CMD + cmd

    local(cmd)


@task
def celery_broker():
    cmd = 'celery -A application.core.celery worker -c {workers} -B -l INFO'

    cmd = cmd.format(
        workers=PROCESS_WORKERS
    )

    if USE_NEWRELIC:
        cmd = NEWRELIC_CMD + cmd

    local(cmd)


@task
def celery_worker():
    cmd = 'newrelic-admin run-program celery -A application.core.celery worker -c {workers} -l INFO'

    cmd = cmd.format(
        workers=PROCESS_WORKERS
    )

    if USE_NEWRELIC:
        cmd = NEWRELIC_CMD + cmd

    local(cmd)


@task
def release(initial=False):
    if not initial:
        stop()

    local('git st')
    local('git push heroku master')

    local('heroku run python manage.py db upgrade')
    local('heroku run python manage.py syncroles')
    local('heroku run python manage.py clearcache')
    local('heroku run "python manage.py assets --parse-templates build && python manage.py collectstatic"')

    start()


@task
def logs():
    local('heroku logs --tail')


@task
def view():
    local('heroku open')


@task
def stop():
    local('heroku maintenance:on')
    for name in DYNOS.iterkeys():
        with warn_only():
            local('heroku ps:scale {name}=0'.format(
                name=name
            ))
            sleep(STOP_TIMEOUT)


@task
def start(initial=False):
    for name, dynos in DYNOS.iteritems():
        local('heroku ps:scale {name}={dynos}'.format(
            name=name,
            dynos=dynos
        ))
        sleep(START_TIMEOUT)

    local('heroku maintenance:off')

    view()


@task
def restart():
    stop()
    start()


@task
def status():
    local('heroku ps')


@task
def psql():
    local('heroku pg:psql')


@task
def events():
    local('heroku run celery -A application.core.celery events')


@task
def ssh():
    local('heroku run bash')


@task
def resetdb():
    info = local('heroku config', capture=True).splitlines()
    name = info[0]
    name = name.replace('=', '')
    for part in ['Config', 'Vars']:
        name = name.replace(part, '')
    name = name.strip()

    with warn_only():
        local('heroku addons:remove heroku-postgresql --confirm {name}'.format(
            name=name
        ))

    local('heroku addons:add heroku-postgresql')

    config = local('heroku config', capture=True).splitlines()

    for line in config:
        if 'HEROKU_POSTGRESQL' in line:
            DB_URL = line.split(':')[0].strip()
            break

    local('heroku pg:promote {url}'.format(url=DB_URL))


@task
def create():
    name = ensure_prompt('APPLICATION NAME')

    local('heroku create {name}'.format(
        name=name
    ))

    local('heroku addons:add heroku-postgresql')
    local('heroku addons:add memcachier')
    local('heroku addons:add newrelic')
    local('heroku addons:add pgbackups:auto-month')
    local('heroku addons:add logentries')
    local('heroku addons:add rabbitmq-bigwig')
    local('heroku addons:add rediscloud')
    local('heroku addons:add sentry')
    local('heroku addons:add sendgrid')

    local('heroku config:set DISABLE_COLLECTSTATIC=1')

    AWS_ACCESS_KEY_ID = ensure_prompt('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = ensure_prompt('AWS_SECRET_ACCESS_KEY')
    S3_BUCKET_NAME = ensure_prompt('S3_BUCKET_NAME (static)')
    S3_BUCKET_NAME_MEDIA = ensure_prompt('S3_BUCKET_NAME (media)')

    local('heroku config:set AWS_ACCESS_KEY_ID={value}'.format(
        value=AWS_ACCESS_KEY_ID
    ))
    local('heroku config:set AWS_SECRET_ACCESS_KEY={value}'.format(
        value=AWS_SECRET_ACCESS_KEY
    ))
    local('heroku config:set S3_BUCKET_NAME={value}'.format(
        value=S3_BUCKET_NAME
    ))
    local('heroku config:set S3_BUCKET_NAME_MEDIA={value}'.format(
        value=S3_BUCKET_NAME_MEDIA
    ))

    SECRET_KEY = ensure_prompt('SECRET_KEY')
    SECURITY_PASSWORD_SALT = ensure_prompt('SECURITY_PASSWORD_SALT')

    local('heroku config:set SECRET_KEY={value}'.format(
        value=SECRET_KEY
    ))
    local('heroku config:set SECURITY_PASSWORD_SALT={value}'.format(
        value=SECURITY_PASSWORD_SALT
    ))

    release(initial=True)


@task
def config():
    local('heroku config')
