from __future__ import absolute_import, division, unicode_literals

from flask import g, Blueprint, render_template, redirect, url_for, flash
from flask.ext.security import login_user, logout_user
from flask.ext.babelex import lazy_gettext as _

from ...mixins import BaseView
from ...decorators import login_session_required, anonymous_user_required
from ...utils import b
from .forms import UserLoginForm, TokenDeactivateForm
from .repository import token_storage


blueprint = Blueprint('auth', __name__,)


class LoginView(BaseView):
    methods = ['GET', 'POST']

    @anonymous_user_required
    def dispatch_request(self):
        form = UserLoginForm()

        if form.validate_on_submit():
            login_user(form.user)

            flash(_('You were successfully logged in.'), 'success')

            return redirect(url_for('index.index'))

        return render_template('auth/login.html', form=form)


class LogoutView(BaseView):
    methods = ['GET', 'POST']

    @login_session_required
    def dispatch_request(self):
        logout_user()

        flash(_('You were successfully logged out.'), 'success')

        return redirect(url_for('index.index'))


class TokenListView(BaseView):
    methods = ['GET']

    @login_session_required
    def dispatch_request(self):
        tokens = token_storage.filter(user=g.user)

        return render_template('auth/token_list.html', tokens=tokens)


class TokenDeactivateView(BaseView):
    methods = ['POST']

    @login_session_required
    def dispatch_request(self):
        form = TokenDeactivateForm()

        if form.validate_on_submit():
            token_storage.delete(token=form.token.data)

            flash(_('Token has has been successfully deactivated.'), 'success')

        else:
            for error in form.errors['token']:
                flash(error, 'danger')

        return redirect(url_for('auth.token_list'))


blueprint.add_url_rule(
    '/login', view_func=LoginView.as_view(
        b('login')
    )
)
blueprint.add_url_rule(
    '/logout', view_func=LogoutView.as_view(
        b('logout')
    )
)
blueprint.add_url_rule(
    '/tokens', view_func=TokenListView.as_view(
        b('token_list')
    )
)
blueprint.add_url_rule(
    '/tokens/deactivate', view_func=TokenDeactivateView.as_view(
        b('token_deactivate')
    )
)
