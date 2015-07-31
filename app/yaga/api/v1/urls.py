from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.conf.urls import include, patterns, url

from . import views
from ...utils import uuid_re

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

posts_urlpatterns = patterns(
    '',
    url(
        r'^(?P<post_id>{uuid_re})/$'.format(uuid_re=uuid_re),
        views.PostRetrieveAPIView.as_view(),
        name='detail'
    ),
)

post_urlpatterns = patterns(
    '',
    url(
        r'^$',
        views.PostCreateAPIView.as_view(),
        name='create'
    ),
    url(
        r'^(?P<post_id>{uuid_re})/like/$'.format(uuid_re=uuid_re),
        views.LikeCreateDestroyAPIView.as_view(),
        name='like'
    ),
    url(
        r'^(?P<post_id>{uuid_re})/copy/$'.format(uuid_re=uuid_re),
        views.PostCopyUpdateAPIView.as_view(),
        name='copy'
    ),
    url(
        r'^(?P<post_id>{uuid_re})/$'.format(uuid_re=uuid_re),
        views.PostRetrieveUpdateDestroyAPIView.as_view(),
        name='detail'
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
        r'^(?P<group_id>{uuid_re})/$'.format(uuid_re=uuid_re),
        views.GroupRetrieveUpdateAPIView.as_view(),
        name='retrieve-update'
    ),
    url(
        r'^(?P<group_id>{uuid_re})/mute/$'.format(uuid_re=uuid_re),
        views.GroupMemberMuteAPIView.as_view(),
        name='mute'
    ),
    url(
        r'^(?P<group_id>{uuid_re})/join/$'.format(uuid_re=uuid_re),
        views.GroupMemberJoinUpdateAPIView.as_view(),
        name='join'
    ),
    url(
        r'^(?P<group_id>{uuid_re})/members/$'.format(uuid_re=uuid_re),
        views.GroupMemberUpdateDestroyAPIView.as_view(),
        name='members'
    ),
    url(
        r'^(?P<group_id>{uuid_re})/posts/'.format(uuid_re=uuid_re),
        include(post_urlpatterns, namespace='posts')
    ),
    url(
        r'^discover/$',
        views.GroupDiscoverListAPIView.as_view(),
        name='discover'
    ),
    url(
        r'^public/$',
        views.PublicGroupListAPIView.as_view(),
        name='public'
    ),
    url(
        r'^(?P<group_id>{uuid_re})/list/'.format(uuid_re=uuid_re),
        views.PublicGroupGroupRetrieveAPIView.as_view(),
        name='list'
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
        include(group_urlpatterns, namespace='groups')
    ),
    url(
        r'^posts/',
        include(posts_urlpatterns, namespace='posts')
    ),
)
