from __future__ import absolute_import, division, unicode_literals

from appconf import AppConf
from django.conf import settings  # noqa


class ContentAppConf(
    AppConf
):
    GA_ID = 'XXXXX'

    class Meta:
        prefix = 'content'
