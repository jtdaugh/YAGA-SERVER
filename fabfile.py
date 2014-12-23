from __future__ import (
    absolute_import, division, unicode_literals, print_function
)

from time import sleep

from fabric.api import local, task, warn_only, lcd
from fabric.operations import prompt


APP_DIR = 'app'
PROCESS_WORKERS = 2
DYNOS = {
    'web': 1,
    'celery_broker': 1,
    'celery_worker': 0,
}
USE_NEWRELIC = True
# STOP_TIMEOUT = 30
# START_TIMEOUT = 30
STOP_TIMEOUT = 0
START_TIMEOUT = 0
HTTP_TIMEOUT = 30

NEWRELIC_CMD = 'newrelic-admin run-program '


def ensure_prompt(label):
    value = None

    label = '{label}: '.format(
        label=label
    )

    while not value:
        value = prompt(label).strip()

    return value


@task
def uwsgi():
    cmd = 'uwsgi --module=app.wsgi:application --http-keepalive=0 --master --processes={workers} --harakiri=30 --vacuum --single-interpreter --enable-threads --http :$PORT'

    cmd = cmd.format(
        workers=PROCESS_WORKERS,
        timeout=HTTP_TIMEOUT
    )

    if USE_NEWRELIC:
        cmd = NEWRELIC_CMD + cmd

    with lcd(APP_DIR):
        local(cmd)


@task
def gunicorn():
    cmd = 'gunicorn app.wsgi:application --keep-alive=0 --workers={workers} --timeout={timeout} --preload --access-logfile=- --error-logfile=-'

    cmd = cmd.format(
        workers=PROCESS_WORKERS,
        timeout=HTTP_TIMEOUT
    )

    if USE_NEWRELIC:
        cmd = NEWRELIC_CMD + cmd

    with lcd(APP_DIR):
        local(cmd)


@task
def celery_broker():
    cmd = 'celery -A app worker -c {workers} -B'

    cmd = cmd.format(
        workers=PROCESS_WORKERS
    )

    if USE_NEWRELIC:
        cmd = NEWRELIC_CMD + cmd

    with lcd(APP_DIR):
        local(cmd)


@task
def celery_worker():
    cmd = 'run-program celery -A app worker -c {workers}'

    cmd = cmd.format(
        workers=PROCESS_WORKERS
    )

    if USE_NEWRELIC:
        cmd = NEWRELIC_CMD + cmd

    with lcd(APP_DIR):
        local(cmd)


@task
def deploy():
    with lcd(APP_DIR):
        local('python manage.py clear_cache')
        local('python manage.py migrate')
        local('python manage.py bower_install -- --config.interactive=false')
        local('python manage.py collectstatic --noinput')
        local('python manage.py clean_compress')
        local('python manage.py compress')


@task
def release(initial=False):
    if not initial:
        stop()

    local('git st')
    local('git push heroku master')

    local('heroku run fab deploy')

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
def start():
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
    local('heroku run "cd {app} celery -A app events"'.format(
        app=APP_DIR
    ))


@task
def ssh():
    local('heroku run bash')


@task
def resetdb():
    stop()

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

    local('heroku run "cd {app} && python manage.py migrate"'.format(
        app=APP_DIR
    ))

    start()


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
    local('heroku config:add BUILDPACK_URL=https://github.com/ddollar/heroku-buildpack-multi.git')

    AWS_ACCESS_KEY_ID = ensure_prompt('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = ensure_prompt('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = ensure_prompt('AWS_STORAGE_BUCKET_NAME')

    local('heroku config:set AWS_ACCESS_KEY_ID={value}'.format(
        value=AWS_ACCESS_KEY_ID
    ))
    local('heroku config:set AWS_SECRET_ACCESS_KEY={value}'.format(
        value=AWS_SECRET_ACCESS_KEY
    ))
    local('heroku config:set AWS_STORAGE_BUCKET_NAME={value}'.format(
        value=AWS_STORAGE_BUCKET_NAME
    ))

    SECRET_KEY = ensure_prompt('SECRET_KEY')

    local('heroku config:set SECRET_KEY={value}'.format(
        value=SECRET_KEY
    ))

    release(initial=True)

    print('SET {bucket} CORS'.format(
        bucket=AWS_STORAGE_BUCKET_NAME
    ))
    print('''
<CORSConfiguration>
    <CORSRule>
        <AllowedOrigin>*</AllowedOrigin>
        <AllowedMethod>PUT</AllowedMethod>
        <AllowedMethod>POST</AllowedMethod>
        <AllowedMethod>GET</AllowedMethod>
        <MaxAgeSeconds>3000</MaxAgeSeconds>
        <AllowedHeader>*</AllowedHeader>
    </CORSRule>
</CORSConfiguration>
''')


@task
def config():
    local('heroku config')


@task
def shell():
    local('heroku run "cd {app} && python manage.py shell_plus"'.format(
        app=APP_DIR
    ))
