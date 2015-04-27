from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.conf.urls import include, patterns, url

from .api.v1.urls import urlpatterns as api_urlpatterns_v1
from .views.group.views import GroupBaseRedirectView, GroupListView
from .views.post.views import PostBaseRedirectView, PostListView
from .views.stats.views import BasicStatsTemplateView, StatsBaseRedirectView
from .views.user import views as user_view

api_urlpatterns = patterns(
    '',
    url(
        r'^v1/',
        include(api_urlpatterns_v1, namespace='v1')
    ),
)

stats_urlpatterns = patterns(
    '',
    url(
        r'^$',
        StatsBaseRedirectView.as_view(),
        name='base'
    ),
    url(
        r'^basic/$',
        BasicStatsTemplateView.as_view(),
        name='basic'
    )
)

user_urlpatterns = patterns(
    '',
    url(
        r'^$',
        user_view.UserBaseRedirectView.as_view(),
        name='base'
    ),
    url(
        r'^list/$',
        user_view.UserListView.as_view(),
        name='list'
    ),
    url(
        r'^list/(?P<user_id>[\-a-z0-9]{32,36})/$',
        user_view.UserUpdateView.as_view(),
        name='detail'
    )
)

post_urlpatterns = patterns(
    '',
    url(
        r'^$',
        PostBaseRedirectView.as_view(),
        name='base'
    ),
    url(
        r'^list/$',
        PostListView.as_view(),
        name='list'
    ),
)

group_urlpatterns = patterns(
    '',
    url(
        r'^$',
        GroupBaseRedirectView.as_view(),
        name='base'
    ),
    url(
        r'^list/$',
        GroupListView.as_view(),
        name='list'
    ),
)

urlpatterns = patterns(
    '',
    url(
        r'^$',
        StatsBaseRedirectView.as_view(),
        name='stats_base_redirec'
    ),
    url(
        r'^api/',
        include(api_urlpatterns, namespace='api')
    ),
    url(
        r'^stats/',
        include(stats_urlpatterns, namespace='stats')
    ),
    url(
        r'^user/',
        include(user_urlpatterns, namespace='user')
    ),
    url(
        r'^post/',
        include(post_urlpatterns, namespace='post')
    ),
    url(
        r'^group/',
        include(group_urlpatterns, namespace='group')
    )
)
