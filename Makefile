ENV_DIR=env
CMD_ENV=virtualenv
CMD_ACTIVATE_ENV=source $(ENV_DIR)/bin/activate
CMD_DEPLOY=fab deploy


install:
	test -d $(ENV_DIR) || $(CMD_ENV) $(ENV_DIR)
	$(CMD_ACTIVATE_ENV); $(CMD_DEPLOY)

all: install

