from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.db import transaction
from django.http import HttpResponseServerError
from django.shortcuts import render
from django.template import Context, loader
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django_filters.views import FilterView
from rest_framework.permissions import SAFE_METHODS
from django.http import HttpResponsePermanentRedirect

from .utils import cache_view, crispy_filter_helper, user_cache_view


def csrf(request, reason=''):
    error = _('400')
    return render(request, 'csrf.html', {'error': error}, status=400)


def handler400(request):
    error = _('400')
    return render(request, '400.html', {'error': error}, status=400)


def handler403(request):
    error = _('403')
    return render(request, '403.html', {'error': error}, status=403)


def handler404(request):
    # error = _('404')
    # return render(request, '404.html', {'error': error}, status=404)
    return HttpResponsePermanentRedirect('/')

def handler500(request):
    template = loader.get_template('500.html')
    return HttpResponseServerError(template.render(Context({})))


class UserCacheView(
    object
):
    @method_decorator(user_cache_view)
    def dispatch(self, request, *args, **kwargs):
        return super(UserCacheView, self).dispatch(request, *args, **kwargs)


class CacheView(
    object
):
    @method_decorator(cache_view)
    def dispatch(self, request, *args, **kwargs):
        return super(CacheView, self).dispatch(request, *args, **kwargs)


class BaseAtomicView(
    object
):
    pass


class AtomicView(
    object
):
    @method_decorator(transaction.atomic)
    def dispatch(self, *args, **kwargs):
        return super(AtomicView, self).dispatch(*args, **kwargs)


class NonAtomicView(
    object
):
    @method_decorator(transaction.non_atomic_requests)
    def dispatch(self, *args, **kwargs):
        return super(NonAtomicView, self).dispatch(*args, **kwargs)


class SafeNonAtomicView(
    object
):
    @method_decorator(transaction.non_atomic_requests)
    def dispatch(self, *args, **kwargs):
        dispatch = super(SafeNonAtomicView, self).dispatch

        if self.request.method not in SAFE_METHODS:
            dispatch = transaction.atomic(dispatch)

        return dispatch(*args, **kwargs)


class CrispyFilterView(
    FilterView
):
    @crispy_filter_helper
    def get(self, request, *args, **kwargs):
        return super(CrispyFilterView, self).get(
            request, *args, **kwargs
        )


class PatchAsPutMixin(
    object
):
    def patch(self, request, *args, **kwargs):
        return super(PatchAsPutMixin, self).put(
            request, *args, **kwargs
        )
