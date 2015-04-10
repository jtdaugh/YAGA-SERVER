from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals
)

from time import sleep

from fabric.api import local, task, warn_only
from fabric.operations import prompt

APP_DIR = 'app'
DYNOS = {
    'web': 1,
    'celery_broker': 1,
    'celery_worker': 0,
    'sqs': 1
}
# STOP_TIMEOUT = 30
# START_TIMEOUT = 30
STOP_TIMEOUT = 0
START_TIMEOUT = 0


def ensure_prompt(label):
    value = None

    label = '{label}: '.format(
        label=label
    )

    while not value:
        value = prompt(label).strip()

    return value


@task
def release(initial=False):
    if not initial:
        stop()

    local('git st')
    local('git push heroku master')

    local('heroku run rake deploy')

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
    # local('heroku pg:psql')
    config = local('heroku config', capture=True).splitlines()

    for line in config:
        if 'HEROKU_POSTGRESQL' in line:
            DB_URL = line.split(' ')[1].strip()
            break

    local('pgcli {url}'.format(
        url=DB_URL
    ))


@task
def events():
    local('heroku run "cd {app} && celery -A app events"'.format(
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
            DB_NAME = line.split(':')[0].strip()
            break

    local('heroku pg:promote {name}'.format(name=DB_NAME))

    # local('heroku run "cd {app} && python manage.py migrate"'.format(
    #     app=APP_DIR
    # ))

    # start()


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

    AWS_REGION = ensure_prompt('AWS_REGION')
    AWS_ACCESS_KEY_ID = ensure_prompt('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = ensure_prompt('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = ensure_prompt('AWS_STORAGE_BUCKET_NAME')
    AWS_SQS_QUEUE = ensure_prompt('AWS_SQS_QUEUE')

    local('heroku config:set AWS_REGION={value}'.format(
        value=AWS_REGION
    ))
    local('heroku config:set AWS_ACCESS_KEY_ID={value}'.format(
        value=AWS_ACCESS_KEY_ID
    ))
    local('heroku config:set AWS_SECRET_ACCESS_KEY={value}'.format(
        value=AWS_SECRET_ACCESS_KEY
    ))
    local('heroku config:set AWS_STORAGE_BUCKET_NAME={value}'.format(
        value=AWS_STORAGE_BUCKET_NAME
    ))
    local('heroku config:set AWS_SQS_QUEUE={value}'.format(
        value=AWS_SQS_QUEUE
    ))

    APNS_MODE = ensure_prompt('APNS_MODE')

    local('heroku config:set APNS_MODE={value}'.format(
        value=APNS_MODE
    ))

    SECRET_KEY = ensure_prompt('SECRET_KEY')

    local('heroku config:set SECRET_KEY={value}'.format(
        value=SECRET_KEY
    ))

    DOMAIN = ensure_prompt('DOMAIN (http domain for dashboard)')

    local('heroku config:set DOMAIN={value}'.format(
        value=DOMAIN
    ))

    release(initial=True)

    print('SET {bucket} CORS'.format(
        bucket=AWS_STORAGE_BUCKET_NAME
    ))
    print('''
<?xml version="1.0" encoding="UTF-8"?>
<CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <CORSRule>
        <AllowedOrigin>*</AllowedOrigin>
        <AllowedMethod>PUT</AllowedMethod>
        <AllowedMethod>POST</AllowedMethod>
        <AllowedMethod>GET</AllowedMethod>
        <MaxAgeSeconds>3000</MaxAgeSeconds>
        <AllowedHeader>*</AllowedHeader>
    </CORSRule>
</CORSConfiguration>

{
  "Version": "2008-10-17",
  "Id": "arn:aws:sqs:us-west-1:609367773239:yaga-dev/SQSDefaultPolicy",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "SQS:SendMessage",
      "Resource": "arn:aws:sqs:us-west-1:609367773239:yaga-dev",
      "Condition": {
        "ArnLike": {
          "aws:SourceArn": "arn:aws:s3:*:*:yaga-dev"
        }
      }
    }
  ]
}
''')


@task
def config():
    local('heroku config')


@task
def shell():
    local('heroku run "cd {app} && python manage.py shell_plus"'.format(
        app=APP_DIR
    ))


@task
def superuser():
    local('heroku run "cd {app} && python manage.py createsuperuser"'.format(
        app=APP_DIR
    ))
