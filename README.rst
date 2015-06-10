yaga server
===========

Development version `http://yaga-dev.heroku.com/ <http://yaga-dev.heroku.com/>`_

Installation Mac OS X:
**********************

.. code-block:: bash

    brew install gettext pkg-config libffi libxml2 libxslt libevent bcrypt rabbitmq redis memcached postgresql libmemcached ffmpeg gifsicle imagemagick node

    sudo pip install virtualenv

    # bootstrap application
    make install

Development:
************

.. code-block:: bash

    # development server
    make runserver

    # background tasks
    make celery

    # create superuser
    make superuser

Visit `http://127.0.0.1:8000/ <http://127.0.0.1:8000/>`_

Tests:
******

.. code-block:: bash

    # code style check
    make lint

    # run tests
    make test

Deployment:
***********

.. code-block:: bash

    # create new heroku application
    fab create

    # release latest code to heroku
    fab release

    # view application logs
    fab logs

    # view application status
    fab status

    # open application via web-browser
    fab view

    # stop application
    fab stop

    # start application
    fab start

    # restart application
    fab restart

    # connect to heroku via ssh
    fab ssh

    # connect to heroku postgres psql shell
    fab psql

    # connect to heroku application shell
    fab shell

    # reset heroku database
    fab resetdb
