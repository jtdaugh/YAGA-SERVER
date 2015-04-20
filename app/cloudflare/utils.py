from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import logging

from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address
from django.db import transaction
from django.utils import timezone
from netaddr import IPAddress, IPNetwork

from app.utils import get_requests_session

from .conf import settings
from .models import Mask

logger = logging.getLogger(__name__)


class CloudFlareMask(
    object
):
    def __init__(self):
        self.session = get_requests_session()

        self.load_local()

    def load_local(self):
        self._last_load = timezone.now()
        self._masks = Mask.objects.all().values_list('value', flat=True)

    @property
    def masks(self):
        if (
            self._last_load + settings.CLOUDFLARE_LOAD_RUN_EVERY
            >
            timezone.now()
        ):
            self.load_local()

        return self._masks

    def is_valid_remote_addr(self, remote_addr):
        if not remote_addr:
            return False

        try:
            remote_addr = validate_ipv4_address(remote_addr)
        except ValidationError:
            return False

        return remote_addr

    def is_cloudflare(self, remote_addr):
        remote_addr = self.is_valid_remote_addr(remote_addr)

        if not remote_addr:
            return False

        remote_addr = IPAddress(remote_addr)

        for mask in self.masks:
            try:
                mask = IPNetwork(mask)
            except Exception:
                continue

            if remote_addr in mask:
                return True

        return False

    def load_remote(self):
        masks = []

        try:
            response = self.session.get(settings.CLOUDFLARE_ENDPOINT)

            for mask in response.text.split('\n'):
                try:
                    mask = IPNetwork(mask)
                except Exception:
                    continue

                masks.append(mask)
        except Exception as e:
            logger.exception(e)

        if masks:
            with transaction.atomic():
                for mask in Mask.objects.all():
                    mask.delete()

                for mask in masks:
                    mask = Mask(value=mask)
                    mask.save()


cloudflare_mask = CloudFlareMask()
