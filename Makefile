ENV_DIR=env
CMD_ENV=virtualenv
CMD_PYTHON=python
CMD_CELERY=celery -A application.core.celery worker -c 1 -B -l INFO
CMD_MANAGE=$(CMD_PYTHON) manage.py
CMD_ACTIVATE_ENV=source $(ENV_DIR)/bin/activate
CMD_DEBUG=$(CMD_MANAGE) runserver
CMD_TEST=TESTING=1 nosetests -v --with-coverage
CMD_LINT=flake8 application
CMD_DB_ENSURE=$(CMD_MANAGE) db ensure
CMD_DB_UPGRATE=$(CMD_MANAGE) db upgrade
CMD_SYNCROLES=$(CMD_MANAGE) syncroles
CMD_CLEARCACHE=$(CMD_MANAGE) clearcache
CMD_ASSETS_BUILD=$(CMD_MANAGE) assets --parse-templates build
CMD_ASSETS_WATCH=$(CMD_MANAGE) assets --parse-templates watch
CMD_PIP=pip install -r requirements.txt

debug:
	$(CMD_ACTIVATE_ENV); $(CMD_DEBUG)

celery:
	$(CMD_ACTIVATE_ENV); $(CMD_CELERY)

install:
	test -d $(ENV_DIR) || $(CMD_ENV) $(ENV_DIR)
	$(CMD_ACTIVATE_ENV); $(CMD_PIP)
	$(CMD_ACTIVATE_ENV); $(CMD_DB_ENSURE)
	$(CMD_ACTIVATE_ENV); $(CMD_DB_UPGRATE)
	$(CMD_ACTIVATE_ENV); $(CMD_SYNCROLES)
	$(CMD_ACTIVATE_ENV); $(CMD_CLEARCACHE)
	$(CMD_ACTIVATE_ENV); $(CMD_ASSETS_BUILD)

watch:
	$(CMD_ACTIVATE_ENV); $(CMD_ASSETS_WATCH)

test:
	$(CMD_ACTIVATE_ENV); $(CMD_TEST)

lint:
	$(CMD_ACTIVATE_ENV); $(CMD_LINT)

