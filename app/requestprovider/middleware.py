from __future__ import absolute_import, division, unicode_literals

from django.utils.functional import SimpleLazyObject

from .signals import request_provider


class RequestProviderMiddleware(
    object
):
    def __new__(cls):
        if not hasattr(cls, '_singleton'):
            cls._singleton = super(RequestProviderMiddleware, cls).__new__(cls)
        return cls._singleton

    def __init__(self):
        self.request = None

        request_provider.connect(self)

    def process_request(self, request):
        self.request = None

    def process_view(self, request, view_func, view_args, view_kwargs):
        def lazy_request():
            return request

        self.request = SimpleLazyObject(lazy_request)

    def __call__(self, **kwargs):
        return self.request
