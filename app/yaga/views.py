from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import datetime

from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.views.generic import TemplateView

from .models import Group, Like, Post


class BasicStatsTemplateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    TemplateView
):
    template_name = 'yaga/basic_stats.html'
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
                    date_joined__gte=today,
                    verified=True
                ).count(),
                'groups': Group.objects.filter(
                    created_at__gte=today
                ).count(),
                'posts': Post.objects.filter(
                    created_at__gte=today,
                    ready=True
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
                    ready=True
                ).count(),
                'likes': Like.objects.all().count()
            }
        }

        return context
