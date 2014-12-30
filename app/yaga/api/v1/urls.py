from __future__ import absolute_import, division, unicode_literals

from django.conf.urls import patterns, url, include

from .views import (
    UserRetrieveUpdateAPIView,
    CodeRetrieveAPIView, CodeCreateAPIView,
    TokenCreateDestroyAPIView,
    GroupListCreateAPIView, GroupRetrieveUpdateAPIView,
    GroupManageMemberAddAPIView, GroupManageMemberRemoveAPIView,
    GroupManageMemberMuteAPIView,
    PostCreateAPIView, PostRetrieveAPIView
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
        r'^(?P<group_id>[a-z0-9]{32})/$',
        GroupRetrieveUpdateAPIView.as_view(),
        name='retrieve-update'
    ),
    url(
        r'^(?P<group_id>[a-z0-9]{32})/remove_member/$',
        GroupManageMemberRemoveAPIView.as_view(),
        name='member-remove'
    ),
    url(
        r'^(?P<group_id>[a-z0-9]{32})/add_member/$',
        GroupManageMemberAddAPIView.as_view(),
        name='member-add'
    ),
    url(
        r'^(?P<group_id>[a-z0-9]{32})/mute/$',
        GroupManageMemberMuteAPIView.as_view(),
        name='member-mute'
    ),
    url(
        r'^(?P<group_id>[a-z0-9]{32})/add_post/$',
        PostCreateAPIView.as_view(),
        name='post-add'
    ),
    url(
        r'^(?P<group_id>[a-z0-9]{32})/posts/(?P<post_id>[a-z0-9]{32})/$',
        PostRetrieveAPIView.as_view(),
        name='post-retrieve'
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
        r'^groups/',
        include(group_urlpatterns, namespace='group')
    ),
)
