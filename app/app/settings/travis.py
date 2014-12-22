from __future__ import absolute_import, division, unicode_literals

from app.settings.base import BaseConfiguration, Implementation, Initialization


class TravisConfiguration(
    BaseConfiguration
):
    pass


class TravisImplementation(
    Implementation
):
    pass


class Configuration(
    Initialization,
    TravisImplementation,
    TravisConfiguration
):
    pass
