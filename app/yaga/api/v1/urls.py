from __future__ import absolute_import, division, unicode_literals

from django.conf.urls import patterns, url, include

from .views import (
    UserRetrieveAPIView,
    TokenCreateAPIView,
    CodeCreateAPIView, CodeRetrieveAPIView,
)


auth_urlpatterns = patterns(
    '',
    url(
        r'^about/',
        UserRetrieveAPIView.as_view(),
        name='about'
    ),
    url(
        '^code/request/',
        CodeCreateAPIView.as_view(),
        name='code-request'
    ),
    url(
        '^code/status/',
        CodeRetrieveAPIView.as_view(),
        name='code-status'
    ),
    url(
        '^token/',
        TokenCreateAPIView.as_view(),
        name='token'
    )
)


urlpatterns = patterns(
    '',
    url(
        r'^auth/',
        include(auth_urlpatterns, namespace='auth')
    ),
)
