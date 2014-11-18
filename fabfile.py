from fabric.api import local, task


def manage(cmd):
    local('python manage.py {cmd}'.format(cmd=cmd))


def heroku_manage(cmd):
    local('heroku run python manage.py {cmd}'.format(cmd=cmd))


@task
def deploy():
    local('pip install -r requirements.txt')

    manage('db upgrade')
    manage('syncroles')
    manage('compilemessages')
    manage('assets --parse-templates build')
    manage('collectstatic')


@task
def release():
    local('git st')
    local('git push heroku master')

    heroku_manage('db upgrade')
    heroku_manage('syncroles')
    heroku_manage('assets --parse-templates build')
    heroku_manage('collectstatic')


@task
def watch():
    manage('assets --parse-templates watch')


@task
def runserver():
    manage('runserver')
