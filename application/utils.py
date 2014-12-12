from __future__ import absolute_import, division, unicode_literals

import datetime
import string
from collections import MutableMapping

import phonenumbers
from Crypto.Random.random import choice
from six import binary_type, string_types
from flask import request
from flask.json import JSONEncoder
from speaklater import is_lazy_string


def u(value):
    if isinstance(value, binary_type):
        value = value.decode()

    return value


def b(value):
    if isinstance(value, string_types):
        value = value.encode()

    return value


def get_random_string(length):
    sequence = string.ascii_letters + string.digits

    return ''.join(choice(sequence) for _ in range(length))


def now():
    return datetime.datetime.utcnow()


def dummy_callback(*args, **kwarg):
    pass


def trace():
    import ipdb

    ipdb.set_trace()


def detect_json():
    accept = request.accept_mimetypes.best_match([
        'application/json', 'text/html'
    ])

    return accept == 'application/json'


class BaseJSONEncoder(JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()

        if hasattr(obj, 'to_json'):
            return obj.to_json()

        if hasattr(obj, '__str__'):
            return str(obj)

        # Python 3 ?
        if hasattr(obj, '__unicode__'):
            return unicode(obj)

        if is_lazy_string(obj):
            return str(obj)

        return JSONEncoder.default(self, obj)


class DummyDict(MutableMapping):
    def __getitem__(self, key):
        try:
            return self.__dict__[key]
        except KeyError:
            return None

    def __setitem__(self, key, value):
        self.__dict__[key] = value

        return self[key]

    def __delitem__(self, key):
        try:
            del self.__dict__[key]
        except KeyError:
            pass

    def __iter__(self):
        return self.__dict__.__iter__()

    def __len__(self):
        return self.__dict__.__len__()


class PhoneTools(object):
    def get_country_codes(self):
        _map = {}

        for code, countries in \
                phonenumbers.COUNTRY_CODE_TO_REGION_CODE.items():
            for country in countries:
                if country != '001' and country not in _map:
                    _map[country] = '+{code}'.format(
                        code=code
                    )

        return _map

    def format(self, number):
        if not number.startswith('+'):
            number = '+{number}'.format(
                number=number
            )

        try:
            number = phonenumbers.parse(number)

            if phonenumbers.is_valid_number(number):
                number = phonenumbers.format_number(
                    number, phonenumbers.PhoneNumberFormat.E164
                )
            else:
                number = None
        except:
            number = None

        return number


phone_tools = PhoneTools()
