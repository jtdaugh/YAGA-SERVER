from __future__ import absolute_import, division, unicode_literals

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView

from .forms import SignInForm


class SignInView(
    FormView
):
    form_class = SignInForm
    template_name = 'accounts/sign_in.html'

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(SignInView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(self.get_success_url())
        return super(SignInView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(self.get_success_url())
        return super(SignInView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(SignInView, self).form_valid(form)

    def get_success_url(self):
        if self.success_url:
            redirect_to = self.success_url
        else:
            redirect_to = self.request.REQUEST.get(
                REDIRECT_FIELD_NAME, ''
            )

        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = reverse_lazy(settings.LOGIN_REDIRECT_URL)

        return redirect_to


class SignOutView(
    RedirectView
):
    permanent = False
    query_string = False

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(SignOutView, self).dispatch(request, *args, **kwargs)

    def get_redirect_url(self):
        if self.request.user.is_authenticated():
            logout(self.request)
        return reverse_lazy('accounts:sign_in')
