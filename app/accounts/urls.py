from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from .views import ChangePasswordView, SignInView, SignOutView

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
    url(
        _(r'^change_password/$'),
        ChangePasswordView.as_view(),
        name='change_password'
    )
)
