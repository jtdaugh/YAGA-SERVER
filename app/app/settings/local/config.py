from __future__ import absolute_import, division, unicode_literals

from app.settings.base.config import (
    BaseConfiguration, Implementation, Initialization
)
from app.settings.local.constants import LocalConstants


class LocalConfiguration(
    BaseConfiguration
):
    # -------------------------------------------------------
    # constants configuration
    # -------------------------------------------------------
    CONSTANTS = LocalConstants()


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
