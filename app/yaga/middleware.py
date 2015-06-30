from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.http import HttpResponse
from rest_framework import status

from .choices import VendorChoice
from .conf import settings


class YagaRequest(
    object
):
    def __init__(self, request):
        header = request.META.get(
            settings.YAGA_CLIENT_VERSION_HEADER,
            settings.YAGA_DEFAULT_CLIENT_HEADER
        )

        match = settings.YAGA_CLIENT_RE.match(header)

        if not match:
            match = settings.YAGA_CLIENT_RE.match(
                settings.YAGA_DEFAULT_CLIENT_HEADER
            )

        info = match.groupdict()

        vendort_choice = VendorChoice()

        self.CLIENT_VERSION = int(info['version'])
        self.CLIENT_VENDOR = vendort_choice.key(str(info['vendor']))


def not_supported_client(request):
    return HttpResponse(
        status=status.HTTP_406_NOT_ACCEPTABLE
    )


class YagaMiddleware(
    object
):
    def process_request(self, request):
        request.bridge.yaga = YagaRequest(request)

        if (
            request.bridge.yaga.CLIENT_VERSION
            not in
            settings.YAGA_SUPPORTED_CLIENT_VERSIONS
        ):
            return not_supported_client(request)
