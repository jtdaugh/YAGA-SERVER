from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.conf.urls import include, patterns, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.sitemaps.views import sitemap
from django.db.models import get_models
from django.shortcuts import get_object_or_404
from django.views.i18n import javascript_catalog
from hijack import views as hijack_views
from hijack.helpers import login_user as hijack_login_user
from hijack.urls import urlpatterns as hijack_urlpatterns

from content.sitemaps import IndexSitemap
from content.views import (
    FaviconRedirectView, IndexTemplateView, RobotsTemplateView, WatchVideoView
)

from .conf import settings
from .utils import cache_view

admin.autodiscover()


@staff_member_required
def login_with_id(request, user_id):
    user = get_object_or_404(
        get_user_model(),
        pk=user_id
    )
    return hijack_login_user(request, user)


hijack_views.login_with_id = login_with_id


hijack_login_with_id_urlpattern = url(
    r'^(?P<user_id>[\-a-z0-9]{32,36})/$',
    'hijack.views.login_with_id',
    name='login_with_id'
)

for urlpattern in hijack_urlpatterns:
    if 'user_id' in urlpattern._regex:
        login_with_id_pattern = urlpattern
        break

hijack_urlpatterns.remove(login_with_id_pattern)

hijack_urlpatterns.append(
    hijack_login_with_id_urlpattern
)


if settings.DISABLE_DELETE_SELECTED:
    try:
        admin.site.disable_action('delete_selected')
    except KeyError:
        pass


if settings.MODELS_AUTO_REGISTRATION:
    for model in get_models():
        try:
            admin.site.register(model)
        except AlreadyRegistered:
            pass


handler400 = 'app.views.handler400'
handler403 = 'app.views.handler403'
handler404 = 'app.views.handler404'
handler500 = 'app.views.handler500'


urlpatterns = patterns('')


urlpatterns += patterns(
    '',
    url(
        r'^accounts/',
        include('accounts.urls', namespace='accounts')
    )
)


if settings.DEBUG:
    # static
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
    # media
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )


if settings.USE_DOCS:
    urlpatterns += patterns(
        '',
        url(
            r'^admin/doc/api/',
            include('rest_framework_swagger.urls')
        ),
        url(
            r'^admin/doc/',
            include('django.contrib.admindocs.urls')
        ),
    )


sitemaps = {
    'index': IndexSitemap,
}


js_info_dict = {
    'domain': 'djangojs',
    'packages': [
        'yaga'
    ]
}


urlpatterns += patterns(
    '',
    # sitemap
    url(
        r'^sitemap\.xml$',
        cache_view(sitemap),
        {
            'sitemaps': sitemaps
        },
        name='sitemap'
    ),
    # favicon
    url(
        r'^favicon\.ico$',
        FaviconRedirectView.as_view()
    ),
    # robots
    url(
        r'^robots\.txt$',
        RobotsTemplateView.as_view()
    ),
    # django i18 js
    url(
        r'^jsi18n/$',
        cache_view(javascript_catalog),
        js_info_dict,
        name='djangojs'
    ),
    # admin
    url(
        r'^admin/',
        include(admin.site.urls)
        # include(site.urls)
    ),
    # hijack
    url(
        r'^hijack/',
        include(hijack_urlpatterns)
    ),
    # index
    url(
        r'^$',
        IndexTemplateView.as_view(),
        name='index'
    ),
    # yaga
    url(
        r'^yaga/',
        include('yaga.urls', namespace='yaga')
    ),
    url(
        r'^v/(?P<post_short_id>[A-Za-z0-9]{8})$',
        WatchVideoView.as_view()
    ),
)
