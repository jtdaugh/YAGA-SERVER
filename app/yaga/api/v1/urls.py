from __future__ import absolute_import, division, unicode_literals

from django.conf.urls import patterns, url, include

from .views import (
    UserRetrieveUpdateAPIView,
    CodeRetrieveAPIView, CodeCreateAPIView,
    TokenCreateDestroyAPIView,
    GroupListCreateAPIView, GroupRetrieveUpdateAPIView,
    GroupManageMemberAddAPIView, GroupManageMemberRemoveAPIView,
    GroupManageMemberMuteAPIView
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
        TokenCreateDestroyAPIView.as_view(),
        name='token'
    )
)


user_urlpatterns = patterns(
    '',
    url(
        r'^profile/$',
        UserRetrieveUpdateAPIView.as_view(),
        name='profile'
    ),
)


group_urlpatterns = patterns(
    '',
    url(
        r'^$',
        GroupListCreateAPIView.as_view(),
        name='list-create'
    ),
    url(
        r'^(?P<pk>[a-z0-9]{32})/$',
        GroupRetrieveUpdateAPIView.as_view(),
        name='retrieve-update'
    ),
    url(
        r'^(?P<pk>[a-z0-9]{32})/remove/$',
        GroupManageMemberRemoveAPIView.as_view(),
        name='manage-remove'
    ),
    url(
        r'^(?P<pk>[a-z0-9]{32})/add/$',
        GroupManageMemberAddAPIView.as_view(),
        name='manage-add'
    ),
    url(
        r'^(?P<pk>[a-z0-9]{32})/mute/$',
        GroupManageMemberMuteAPIView.as_view(),
        name='manage-mute'
    ),
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
