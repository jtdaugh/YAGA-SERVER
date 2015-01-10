from __future__ import absolute_import, division, unicode_literals

from django.conf.urls import include, patterns, url

from .api.v1.urls import urlpatterns as api_urlpatterns_v1

api_urlpatterns = patterns(
    '',
    url(
        r'^v1/',
        include(api_urlpatterns_v1, namespace='v1')
    ),
)

urlpatterns = patterns(
    '',
    url(
        r'^api/',
        include(api_urlpatterns, namespace='api')
    )
)
