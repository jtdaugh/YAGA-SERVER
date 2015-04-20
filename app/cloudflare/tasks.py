from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from app import celery

from .conf import settings
from .utils import cloudflare_mask

if settings.CLOUDFLARE_BEHIND:
    class CloudFlareLoadMask(
        celery.PeriodicTask
    ):
        run_every = settings.CLOUDFLARE_LOAD_RUN_EVERY

        def run(self, *args, **kwargs):
            cloudflare_mask.load_remote()
