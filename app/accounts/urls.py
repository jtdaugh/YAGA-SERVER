from __future__ import absolute_import, division, unicode_literals

from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from .views import SignInView, SignOutView


urlpatterns = patterns(
    '',
    url(
        _(r'^sign_in/$'),
        SignInView.as_view(),
        name='sign_in'
    ),
    url(
        _(r'^sign_out/$'),
        SignOutView.as_view(),
        name='sign_out'
    ),
)
