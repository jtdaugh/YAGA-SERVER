#!/usr/bin/env python
from __future__ import absolute_import, division, unicode_literals

import imp
import locale
import os
import sys

from django.utils import six


def fix_locale():
    if not six.PY3:
        imp.reload(sys)
        sys.setdefaultencoding('utf-8')

    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except ValueError:
        locale.setlocale(locale.LC_ALL, ('en_US', 'UTF-8'))


def set_environ():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
    os.environ.setdefault('DJANGO_CONFIGURATION', 'Configuration')


def setup():
    fix_locale()
    set_environ()


def main():
    setup()

    from configurations.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
