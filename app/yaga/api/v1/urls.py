from __future__ import absolute_import, division, unicode_literals

from django.conf.urls import include, patterns, url

from .views import (
    CodeCreateAPIView,
    CodeRetrieveAPIView,
    GroupListCreateAPIView,
    GroupManageMemberAddAPIView,
    GroupManageMemberMuteAPIView,
    GroupManageMemberRemoveAPIView,
    GroupRetrieveUpdateAPIView,
    LikeCreateDestroyAPIView,
    PostCreateAPIView,
    PostRetrieveUpdateDestroyAPIView,
    TokenCreateAPIView,
    TokenDestroyAPIView,
    UserRetrieveUpdateAPIView
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
        r'^obtain/$',
        TokenCreateAPIView.as_view(),
        name='obtain'
    ),
    url(
        r'^release/$',
        TokenDestroyAPIView.as_view(),
        name='release'
    ),
)


user_urlpatterns = patterns(
    '',
    url(
        r'^profile/$',
        UserRetrieveUpdateAPIView.as_view(),
        name='profile'
    ),
)

post_urlpatterns = patterns(
    '',
    url(
        r'^$',
        PostCreateAPIView.as_view(),
        name='add'
    ),
    url(
        r'^(?P<post_id>[\-a-z0-9]{32,36})/like/$',
        LikeCreateDestroyAPIView.as_view(),
        name='like'
    ),
    url(
        r'^(?P<post_id>[\-a-z0-9]{32,36})/$',
        PostRetrieveUpdateDestroyAPIView.as_view(),
        name='detail'
    ),
)

member_urlpatterns = patterns(
    '',
    url(
        r'^remove/$',
        GroupManageMemberRemoveAPIView.as_view(),
        name='remove'
    ),
    url(
        r'^add/$',
        GroupManageMemberAddAPIView.as_view(),
        name='add'
    )
)


group_urlpatterns = patterns(
    '',
    url(
        r'^$',
        GroupListCreateAPIView.as_view(),
        name='list-create'
    ),
    url(
        r'^(?P<group_id>[\-a-z0-9]{32,36})/$',
        GroupRetrieveUpdateAPIView.as_view(),
        name='retrieve-update'
    ),
    url(
        r'^(?P<group_id>[\-a-z0-9]{32,36})/mute/$',
        GroupManageMemberMuteAPIView.as_view(),
        name='mute'
    ),
    url(
        r'^(?P<group_id>[\-a-z0-9]{32,36})/members/',
        include(member_urlpatterns, namespace='members')
    ),
    url(
        r'^(?P<group_id>[\-a-z0-9]{32,36})/posts/',
        include(post_urlpatterns, namespace='posts')
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
        r'^groups/',
        include(group_urlpatterns, namespace='group')
    ),
)
