from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.conf.urls import include, patterns, url

from . import views

auth_urlpatterns = patterns(
    '',
    url(
        r'^status/$',
        views.CodeRetrieveAPIView.as_view(),
        name='status'
    ),
    url(
        r'^request/$',
        views.CodeCreateAPIView.as_view(),
        name='request'
    ),
    url(
        r'^obtain/$',
        views.TokenCreateAPIView.as_view(),
        name='obtain'
    ),
    url(
        r'^release/$',
        views.TokenDestroyAPIView.as_view(),
        name='release'
    ),
)


user_urlpatterns = patterns(
    '',
    url(
        r'^profile/$',
        views.UserRetrieveUpdateAPIView.as_view(),
        name='profile'
    ),
    url(
        r'^device/$',
        views.DeviceCreateAPIView.as_view(),
        name='device'
    ),
    url(
        r'^search/$',
        views.ContactListCreateAPIView.as_view(),
        name='search'
    )
)

post_urlpatterns = patterns(
    '',
    url(
        r'^$',
        views.PostCreateAPIView.as_view(),
        name='create'
    ),
    url(
        r'^(?P<post_id>[\-a-z0-9]{32,36})/like/$',
        views.LikeCreateDestroyAPIView.as_view(),
        name='like'
    ),
    url(
        r'^(?P<post_id>[\-a-z0-9]{32,36})/$',
        views.PostRetrieveUpdateDestroyAPIView.as_view(),
        name='detail'
    ),
    url(
        r'^(?P<post_id>[\-a-z0-9]{32,36})/likers/$',
        views.LikeListAPIView.as_view(),
        name='likers'
    ),
)

members_urlpatterns = patterns(
    '',
    url(
        r'^remove/$',
        views.GroupManageMemberRemoveAPIView.as_view(),
        name='remove'
    ),
    url(
        r'^add/$',
        views.GroupManageMemberAddAPIView.as_view(),
        name='add'
    )
)


group_urlpatterns = patterns(
    '',
    url(
        r'^$',
        views.GroupListCreateAPIView.as_view(),
        name='list-create'
    ),
    url(
        r'^(?P<group_id>[\-a-z0-9]{32,36})/$',
        views.GroupRetrieveUpdateAPIView.as_view(),
        name='retrieve-update'
    ),
    url(
        r'^(?P<group_id>[\-a-z0-9]{32,36})/mute/$',
        views.GroupManageMemberMuteAPIView.as_view(),
        name='mute'
    ),
    url(
        r'^(?P<group_id>[\-a-z0-9]{32,36})/members/',
        include(members_urlpatterns, namespace='members')
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
        include(group_urlpatterns, namespace='groups')
    ),
)
