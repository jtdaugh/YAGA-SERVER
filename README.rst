yaga server
===========

Development version `http://yaga-dev.heroku.com/ <http://yaga-dev.heroku.com/>`_

Installation Mac OS X:
**********************

.. code-block:: bash

    brew install gettext pkg-config libffi libxml2 libxslt libevent rabbitmq redis memcached bcrypt

    # rabbitmq
    ln -sfv /usr/local/opt/rabbitmq/*.plist ~/Library/LaunchAgents
    launchctl load ~/Library/LaunchAgents/homebrew.mxcl.rabbitmq.plist
    # or rabbitmq-server

    # redis
    ln -sfv /usr/local/opt/redis/*.plist ~/Library/LaunchAgents
    launchctl load ~/Library/LaunchAgents/homebrew.mxcl.redis.plist
    # or redis-server /usr/local/etc/redis.conf

    # memcached
    ln -sfv /usr/local/opt/memcached/*.plist ~/Library/LaunchAgents
    launchctl load ~/Library/LaunchAgents/homebrew.mxcl.memcached.plist
    # or /usr/local/opt/memcached/bin/memcached

    # postgresql
    ln -sfv /usr/local/opt/postgresql/*.plist ~/Library/LaunchAgents
    launchctl load ~/Library/LaunchAgents/homebrew.mxcl.postgresql.plist
    # or postgres -D /usr/local/var/postgres

    # virtualenv
    sudo pip install virtualenv

    # bootstrap application
    make install

Back-end development:
*********************

.. code-block:: bash

    # development server
    make debug

    # background tasks
    make celery

Visit `http://127.0.0.1:5000/ <http://127.0.0.1:5000/>`_


Front-end development:
**********************

.. code-block:: bash

    # code style check
    make watch


Tests:
******

.. code-block:: bash

    # code style check
    make lint

    # run tests
    make test