from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.conf.urls import include, patterns, url

from .api.v1.urls import urlpatterns as api_urlpatterns_v1
from .views.stats.views import BasicStatsTemplateView, StatsBaseRedirectView
from .views.user.views import UserBaseRedirectView, UserListView
from .views.post.views import PostBaseRedirectView, PostListView

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
        UserBaseRedirectView.as_view(),
        name='base'
    ),
    url(
        r'^list/$',
        UserListView.as_view(),
        name='list'
    ),
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
    )
)
