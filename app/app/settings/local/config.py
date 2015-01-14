from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from ..base.config import BaseConfiguration, Implementation, Initialization


class LocalConfiguration(
    BaseConfiguration
):
    pass


class LocalImplementation(
    Implementation
):
    pass


class Configuration(
    Initialization,
    LocalConfiguration,
    LocalImplementation
):
    pass
