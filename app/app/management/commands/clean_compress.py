from __future__ import absolute_import, division, unicode_literals

import os

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.core.files.storage import get_storage_class


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
        except:
            pass
