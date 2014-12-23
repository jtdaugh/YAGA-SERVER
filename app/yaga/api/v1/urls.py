from __future__ import absolute_import, division, unicode_literals

from django.conf.urls import patterns, url, include

from .views import (
    UserRetrieveAPIView, UserUpdateAPIView,
    CodeRetrieveAPIView, CodeCreateAPIView,
    TokenCreateAPIView,
    GroupListAPIView, GroupRetrieveUpdateAPIView,
    GroupCreateAPIView, GroupAddUpdateAPIView,
    GroupDeleteUpdateAPIView,
)


auth_urlpatterns = patterns(
    '',
    url(
        r'^status/$',
        CodeRetrieveAPIView.as_view(),
        name='status'
    ),
    url(
        r'^request/$',
        CodeCreateAPIView.as_view(),
        name='request'
    ),
    url(
        r'^token/$',
        TokenCreateAPIView.as_view(),
        name='token'
    )
)


user_urlpatterns = patterns(
    '',
    url(
        r'^info/$',
        UserRetrieveAPIView.as_view(),
        name='info'
    ),
    url(
        r'^profile/$',
        UserUpdateAPIView.as_view(),
        name='profile'
    ),
)


group_urlpatterns = patterns(
    '',
    url(
        r'^$',
        GroupListAPIView.as_view(),
        name='list'
    ),
    url(
        r'^(?P<pk>[0-9]+)/$',
        GroupRetrieveUpdateAPIView.as_view(),
        name='retrieve'
    ),
    url(
        r'^(?P<pk>[0-9]+)/add/$',
        GroupAddUpdateAPIView.as_view(),
        name='add'
    ),
    url(
        r'^(?P<pk>[0-9]+)/delete/$',
        GroupDeleteUpdateAPIView.as_view(),
        name='delete'
    ),
    url(
        r'^create/$',
        GroupCreateAPIView.as_view(),
        name='create'
    )
)


urlpatterns = patterns(
    '',
    url(
        r'^auth/',
        include(auth_urlpatterns, namespace='auth')
    ),
    url(
        r'^user/',
        include(user_urlpatterns, namespace='user')
    ),
    url(
        r'^group/',
        include(group_urlpatterns, namespace='group')
    ),
)
