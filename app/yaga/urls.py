from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.conf.urls import include, patterns, url

from .api.v1.urls import urlpatterns as api_urlpatterns_v1
from .utils import uuid_re
from .views.group import views as group_view
from .views.post import views as post_view
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
        r'^list/(?P<user_id>{uuid_re})/update/$'.format(uuid_re=uuid_re),
        user_view.UserUpdateView.as_view(),
        name='update'
    )
)

post_urlpatterns = patterns(
    '',
    url(
        r'^$',
        post_view.PostBaseRedirectView.as_view(),
        name='base'
    ),
    url(
        r'^list/$',
        post_view.PostListView.as_view(),
        name='list'
    ),
    url(
        r'^approve/$',
        post_view.PostApproveFormView.as_view(),
        name='approve'
    ),
    url(
        r'^reject/$',
        post_view.PostRejectFormView.as_view(),
        name='reject'
    ),
    url(
        r'^list/(?P<post_id>{uuid_re})/delete/$'.format(uuid_re=uuid_re),
        post_view.PostDeleteView.as_view(),
        name='delete'
    ),
    url(
        r'^list/(?P<post_id>{uuid_re})/update/$'.format(uuid_re=uuid_re),
        post_view.PostUpdateView.as_view(),
        name='update'
    )
)

group_urlpatterns = patterns(
    '',
    url(
        r'^$',
        group_view.GroupBaseRedirectView.as_view(),
        name='base'
    ),
    url(
        r'^list/$',
        group_view.GroupListView.as_view(),
        name='list'
    ),
    url(
        r'^list/(?P<group_id>{uuid_re})/$'.format(uuid_re=uuid_re),
        group_view.GroupDetailView.as_view(),
        name='detail'
    ),    
    url(
        r'^list/(?P<group_id>{uuid_re})/wipe/$'.format(uuid_re=uuid_re),
        group_view.GroupWipeDeleteView.as_view(),
        name='wipe'
    ),
)

urlpatterns = patterns(
    '',
    url(
        r'^$',
        StatsBaseRedirectView.as_view(),
        name='stats_base_redirect'
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
