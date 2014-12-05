from __future__ import absolute_import, division, unicode_literals

from functools import wraps
from copy import copy

from flask import json


def create_json_client(app, client):
    def json_request(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            kwargs['headers'] = [
                ('Accept', 'application/json'),
                ('Content-Type', 'application/json')
            ]

            if kwargs.get('token'):
                kwargs['headers '].append(
                    (app.config['AUTH_HEADER_NAME'], kwargs['token'])
                )

            if kwargs.get('data'):
                kwargs['data'] = json.dumps(kwargs['data'])

                kwargs['headers'].append(
                    ('Content-Length', len(kwargs['data']))
                )

            return fn(*args, **kwargs)

        return wrapper

    json_client = copy(client)

    for method in ['GET', 'HEAD', 'POST', 'PUT', 'DELETE']:
        method = method.lower()

        fn = getattr(json_client, method)

        fn = json_request(fn)

        setattr(json_client, method, fn)

    return json_client
