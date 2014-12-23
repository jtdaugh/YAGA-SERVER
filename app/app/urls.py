from __future__ import absolute_import, division, unicode_literals

from django.conf.urls import patterns, include, url
from django.db.models import get_models
from django.contrib.admin.sites import AlreadyRegistered
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.views.i18n import javascript_catalog

from app.utils import cache_view
from content.views import (
    IndexTemplateView,
    RobotsTemplateView,
    FaviconRedirectView
)
from content.sitemaps import IndexSitemap


admin.autodiscover()


# if settings.DISABLE_DELETE_SELECTED:
#     try:
#         admin.site.disable_action('delete_selected')
#     except KeyError:
#         pass


if settings.MODELS_AUTO_REGISTRATION:
    for model in get_models():
        try:
            admin.site.register(model)
        except AlreadyRegistered:
            pass


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


if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns += patterns(
        '',
        url(
            r'^__debug__/',
            include(debug_toolbar.urls)
        ),
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
    'packages': []
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
)
