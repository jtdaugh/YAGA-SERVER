from __future__ import absolute_import, division, unicode_literals

import base64
import binascii
import datetime
import string
from collections import MutableMapping

import requests
import phonenumbers
from flask import current_app as app
from Crypto.Random.random import choice
from Crypto.Cipher import AES
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


def get_cipher():
    return AES.new(
        app.config['CRYPT_KEY'],
        AES.MODE_CFB,
        app.config['CRYPT_IV']
    )


def encrypt(data):
    try:
        return binascii.hexlify(base64.b64encode(get_cipher().encrypt(data)))
    except:
        return None


def get_locale_string(locale):
    return app.config['LOCALE_MAP'][locale]


def decrypt(data):
    try:
        return get_cipher().decrypt(base64.b64decode(binascii.unhexlify(data)))
    except:
        return None


def setup_http_session(session, app):
    adapter = requests.adapters.HTTPAdapter(
        max_retries=app.config['HTTP_RETRIES']
    )

    session.mount('http://', adapter)
    session.mount('https://', adapter)


def get_http_session(app):
    session = requests.Session()

    setup_http_session(session, app)

    return session


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

    def format_E164(self, number):
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
