APP_DIR=app
ENV_DIR=env
CMD_ENV=virtualenv
CMD_PYTHON=python
CMD_CELERY=cd $(APP_DIR) && celery -A app worker -c 1 -B
CMD_MANAGE=cd $(APP_DIR) && $(CMD_PYTHON) manage.py
CMD_RUNSERVER=$(CMD_MANAGE) runserver
CMD_SHELL=$(CMD_MANAGE) shell_plus
CMD_BOWER=$(CMD_MANAGE) bower_install -- --config.interactive=false
CMD_MIGRATE=$(CMD_MANAGE) migrate
CMD_TEST=$(CMD_MANAGE) test
CMD_LINT=flake8 app && isort --check-only -rc app
CMD_PIP=pip install -r requirements.txt
CMD_NPM=npm install
CMD_ACTIVATE_ENV=source $(ENV_DIR)/bin/activate

runserver:
	$(CMD_ACTIVATE_ENV); $(CMD_RUNSERVER)

celery:
	$(CMD_ACTIVATE_ENV); $(CMD_CELERY)

install:
	$(CMD_NPM)
	test -d $(ENV_DIR) || $(CMD_ENV) $(ENV_DIR)
	$(CMD_ACTIVATE_ENV); $(CMD_PIP)
	$(CMD_ACTIVATE_ENV); $(CMD_BOWER)
	$(CMD_ACTIVATE_ENV); $(CMD_MIGRATE)

test:
	$(CMD_ACTIVATE_ENV); $(CMD_TEST)

lint:
	$(CMD_ACTIVATE_ENV); $(CMD_LINT)

shell:
	$(CMD_ACTIVATE_ENV); $(CMD_SHELL)
