from fabric.api import local, task


def manage(cmd):
    local('python manage.py {cmd}'.format(cmd=cmd))


def heroku_run(cmd):
    local('heroku run {cmd}'.format(cmd=cmd))


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

    heroku_run('db upgrade')
    heroku_run('syncroles')
    manage('assets --parse-templates build')
    manage('collectstatic')


@task
def watch():
    manage('assets --parse-templates watch')


@task
def runserver():
    manage('runserver')
