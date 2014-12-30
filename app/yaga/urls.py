from __future__ import absolute_import, division, unicode_literals

from django.conf.urls import patterns, url, include

from .api.v1.urls import urlpatterns as api_urlpatterns_v1

from .views import SignS3TemplateView


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
    ),
    url(
        r'^sign_s3/',
        SignS3TemplateView.as_view()
    ),
)
