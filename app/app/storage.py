from __future__ import absolute_import, division, unicode_literals

from django.conf import settings
from django.core.files.storage import get_storage_class
from storages.backends.s3boto import S3BotoStorage


class S3StaticStorage(
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


class CachedS3BotoStorage(
    S3BotoStorage
):
    def __init__(self, *args, **kwargs):
        super(CachedS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            'compressor.storage.CompressorFileStorage'
        )()

    def save(self, name, content):
        name = super(CachedS3BotoStorage, self).save(name, content)
        self.local_storage._save(name, content)
        return name


class CachedS3StaticStorage(
    CachedS3BotoStorage
):
    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.STATIC_LOCATION
        super(CachedS3StaticStorage, self).__init__(*args, **kwargs)
