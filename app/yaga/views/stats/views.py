from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import datetime

from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from ...models import Group, Like, Post


class StatsBaseRedirectView(
    LoginRequiredMixin,
    RedirectView
):
    permanent = False
    query_string = True

    def get_redirect_url(self):
        return reverse_lazy('yaga:stats:basic')


class BasicStatsTemplateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    TemplateView
):
    template_name = 'yaga/stats/basic.html'
    raise_exception = True
    permission_required = 'app.view_stats'

    def get_context_data(self, **kwargs):
        context = super(
            BasicStatsTemplateView, self
        ).get_context_data(**kwargs)

        today = datetime.datetime.combine(timezone.now(), datetime.time(0))

        context['stats'] = {
            'today': {
                'users': get_user_model().objects.filter(
                    verified_at__gte=today
                ).count(),
                'groups': Group.objects.filter(
                    created_at__gte=today
                ).count(),
                'posts': Post.objects.filter(
                    created_at__gte=today,
                    state__in=[
                        Post.state_choices.UPLOADED,
                        Post.state_choices.READY,
                        Post.state_choices.DELETED
                    ]
                ).count(),
                'likes': Like.objects.filter(
                    created_at__gte=today
                ).count()
            },
            'total': {
                'users': get_user_model().objects.filter(
                    verified=True
                ).count(),
                'groups': Group.objects.all().count(),
                'posts': Post.objects.filter(
                    state__in=[
                        Post.state_choices.UPLOADED,
                        Post.state_choices.READY,
                        Post.state_choices.DELETED
                    ]
                ).count(),
                'likes': Like.objects.all().count()
            }
        }

        return context
