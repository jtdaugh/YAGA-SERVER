from __future__ import absolute_import, division, unicode_literals

from app.settings.base.config import (
    BaseConfiguration, Implementation, Initialization
)


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
    LocalImplementation,
    LocalConfiguration
):
    pass
