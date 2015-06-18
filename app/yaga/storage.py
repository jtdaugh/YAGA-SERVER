from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import boto
from django.core.cache import cache
from django.core.files.storage import default_storage

from .conf import settings


class CacheStorage(
    object
):
    def __init__(self):
        self.ttl = settings.YAGA_CLOUDFRONT_CLEAN_CACHE_KEY_TTL
        self.key = settings.YAGA_CLOUDFRONT_CLEAN_CACHE_KEY

    def get(self):
        value = cache.get(self.key)

        if not value:
            value = []

        return value

    def remove(self, value):
        value = list(set(self.get()) - set(value))

        return cache.set(self.key, value, self.ttl)

    def add(self, value):
        value = list(set(self.get() + value))

        return cache.set(self.key, value, self.ttl)


class CloudfrontStorage(
    object
):
    def __init__(
        self,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    ):
        self.enabled = bool(settings.CLOUDFRONT_HOST)

        if self.enabled:
            self.cache_storage = CacheStorage()

            self.connection = boto.connect_cloudfront(
                aws_access_key_id,
                aws_secret_access_key
            )

            rs = self.connection.get_all_distributions()

            for ds in rs:
                distribution = ds.get_distribution()

                if distribution.domain_name == settings.CLOUDFRONT_HOST:
                    self.distribution = distribution
                    break

    def to_list(self, keys):
        if not isinstance(keys, (list, tuple)):
            keys = [keys]

        keys = list(set(keys))

        return keys

    def schedule(self, keys):
        if self.enabled:
            keys = self.to_list(keys)

            self.cache_storage.add(keys)

    def clean(self):
        if self.enabled:
            keys = self.cache_storage.get()

            if keys:
                self.delete(keys)

                self.cache_storage.remove(keys)

    def delete(self, keys):
        if self.enabled:
            keys = self.to_list(keys)

            absolute_keys = []

            for key in keys:
                key = key.strip('/')

                if not key.startswith(settings.MEDIA_LOCATION.strip('/')):
                    key = default_storage._normalize_name(key)

                absolute_keys.append(key)

            return self.connection.create_invalidation_request(
                self.distribution.id,
                absolute_keys
            )


cloudfront_storage = CloudfrontStorage()
