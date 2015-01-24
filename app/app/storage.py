from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.core.files.storage import get_storage_class
from storages.backends.s3boto import S3BotoStorage

from .conf import settings


class FixedS3BotoStorage(
    object
):
    def url(self, name):
        url = super(FixedS3BotoStorage, self).url(name)
        if name.endswith('/') and not url.endswith('/'):
            url = '{url}/'.format(
                url=url
            )
        return url


class S3StaticStorage(
    FixedS3BotoStorage,
    S3BotoStorage
):
    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.STATIC_LOCATION
        super(S3StaticStorage, self).__init__(*args, **kwargs)


class S3MediaStorage(
    S3BotoStorage
):
    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.MEDIA_LOCATION
        super(S3MediaStorage, self).__init__(*args, **kwargs)


class CachedS3StaticStorage(
    FixedS3BotoStorage,
    S3BotoStorage
):
    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.STATIC_LOCATION
        super(CachedS3StaticStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            'compressor.storage.CompressorFileStorage'
        )()

    def save(self, name, content):
        name = super(CachedS3StaticStorage, self).save(name, content)
        self.local_storage._save(name, content)
        return name
