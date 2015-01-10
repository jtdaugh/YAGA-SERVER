from __future__ import absolute_import, division, unicode_literals

from django.conf import settings  # noqa
from appconf import AppConf


class ContentAppConf(AppConf):
    GA_ID = 'XXXXX'

    class Meta:
        prefix = 'content'
