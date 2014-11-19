ENV_DIR=env
CMD_ENV=virtualenv
CMD_ACTIVATE_ENV=source $(ENV_DIR)/bin/activate
CMD_FAB=fab
CMD_DEPLOY=$(CMD_FAB) deploy
CMD_DEBUG=$(CMD_FAB) debug

install:
	test -d $(ENV_DIR) || $(CMD_ENV) $(ENV_DIR)
	$(CMD_ACTIVATE_ENV); $(CMD_DEPLOY)

debug:
	$(CMD_ACTIVATE_ENV); $(CMD_DEBUG)

all: install

