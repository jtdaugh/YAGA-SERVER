from __future__ import absolute_import, division, unicode_literals

from django.conf.urls import patterns, url, include

from .views import (
    UserRetrieveAPIView, UserUpdateAPIView,
    CodeRetrieveAPIView, CodeCreateAPIView,
    TokenCreateAPIView,
    GroupListCreateAPIView, GroupRetrieveUpdateAPIView,
    GroupManageAddAPIView, GroupManageRemoveAPIView
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
        GroupListCreateAPIView.as_view(),
        name='list-create'
    ),
    url(
        r'^(?P<pk>[0-9]+)/$',
        GroupRetrieveUpdateAPIView.as_view(),
        name='retrieve-update'
    ),
    url(
        r'^(?P<pk>[0-9]+)/remove/$',
        GroupManageRemoveAPIView.as_view(),
        name='manage-remove'
    ),
    url(
        r'^(?P<pk>[0-9]+)/add/$',
        GroupManageAddAPIView.as_view(),
        name='manage-add'
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
