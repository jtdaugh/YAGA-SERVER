from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import os

from django.conf import settings
from django.core.files.storage import get_storage_class
from django.core.management.base import NoArgsCommand


class Command(
    NoArgsCommand
):
    help = 'Clean django-compressor stuff.'

    def handle_noargs(self, **options):
        storage = get_storage_class(settings.COMPRESS_STORAGE)()

        def clean(root):
            for file in storage.listdir(root)[1]:
                storage.delete(os.path.join(
                    root,
                    file
                ))

            for dir in storage.listdir(root)[0]:
                clean(os.path.join(
                    root,
                    dir
                ))

        try:
            clean(settings.COMPRESS_OUTPUT_DIR)
        except Exception:
            pass
