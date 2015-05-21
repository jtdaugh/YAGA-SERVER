from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import boto
from django.core.files.storage import default_storage

from .conf import settings


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

    def delete(self, keys):
        if self.enabled:
            if not isinstance(keys, (list, tuple)):
                keys = [keys]

            keys = list(set(keys))

            absolute_keys = []

            for key in keys:
                key = key.strip('/')

                if not key.startswith(settings.MEDIA_LOCATION.strip('/')):
                    key = default_storage._normalize_name(key)

                absolute_keys.append(key)

            return self.connection.create_invalidation_request(
                self.distribution.id, absolute_keys
            )


cloudfront_storage = CloudfrontStorage()
