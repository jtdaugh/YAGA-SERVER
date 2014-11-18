from time import sleep

from fabric.api import local, task, warn_only
from fabric.operations import prompt


WEB_WORKERS = 1

STOP_TIMEOUT = 5
START_TIMEOUT = 10


def ensure_prompt(label):
    value = None
    label = '{label}: '.format(label=label)

    while not value:
        value = prompt(label)

    return value.strip()


@task
def deploy():
    local('pip install -r requirements.txt')

    local('python manage.py db upgrade')
    local('python manage.py syncroles')
    local('python manage.py assets --parse-templates build')


@task
def release(initial=False):
    if not initial:
        stop()

    local('git st')
    local('git push heroku master')

    local('heroku run python manage.py db upgrade')
    local('heroku run python manage.py syncroles')
    local('heroku run "python manage.py assets --parse-templates build && python manage.py collectstatic"')

    start()


@task
def watch():
    local('python manage.py assets --parse-templates watch')


@task
def debug():
    local('python manage.py runserver')


@task
def shell():
    local('python manage.py shell')


@task
def logs():
    local('heroku logs --tail')


@task
def view():
    local('heroku open')


@task
def stop():
    local('heroku maintenance:on')
    sleep(STOP_TIMEOUT)
    local('heroku ps:scale web=0')


@task
def start(initial=False):
    local('heroku ps:scale web={workers}'.format(workers=WEB_WORKERS))
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
def ssh():
    local('heroku run bash')


@task
def reset_db():
    info = local('heroku config', capture=True).splitlines()
    name = info[0]
    name = name.replace('=', '')
    for part in ['Config', 'Vars']:
        name = name.replace(part, '')
    name = name.strip()

    with warn_only():
        local('heroku addons:remove heroku-postgresql --confirm {name}').format(name=name)

    local('heroku addons:add heroku-postgresql')

    config = local('heroku config', capture=True).splitlines()

    for line in config:
        if 'HEROKU_POSTGRESQL' in line:
            DB_URL = line.split(':')[0].strip()
            break

    local('heroku pg:promote %s' % DB_URL)


@task
def create():
    name = ensure_prompt('APPLICATION NAME')

    local('heroku create {name}'.format(name=name))

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
    S3_BUCKET_NAME = ensure_prompt('S3_BUCKET_NAME')

    local('heroku config:set AWS_ACCESS_KEY_ID={value}'.format(value=AWS_ACCESS_KEY_ID))
    local('heroku config:set AWS_SECRET_ACCESS_KEY={value}'.format(value=AWS_SECRET_ACCESS_KEY))
    local('heroku config:set S3_BUCKET_NAME={value}'.format(value=S3_BUCKET_NAME))

    SECRET_KEY = ensure_prompt('SECRET_KEY')
    SECURITY_PASSWORD_SALT = ensure_prompt('SECURITY_PASSWORD_SALT')

    local('heroku config:set SECRET_KEY={value}'.format(value=SECRET_KEY))
    local('heroku config:set SECURITY_PASSWORD_SALT={value}'.format(value=SECURITY_PASSWORD_SALT))

    release(initial=True)
