from blinker import Namespace
from flask import g


auth = Namespace()
auth_ident = auth.signal('auth_ident')


def on_auth_ident(ident):
    g.auth_ident = ident


auth_ident.connect(on_auth_ident)
