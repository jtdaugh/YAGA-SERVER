from __future__ import absolute_import, division, unicode_literals

import datetime
from binascii import hexlify
from collections import MutableMapping

from Crypto import Random
from six import binary_type, string_types
from flask.json import JSONEncoder as BaseJSONEncoder
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
    random = Random
    random.atfork()
    random = random.new().read
    return hexlify(random(length // 2 + 1))[:length]


def now():
    return datetime.datetime.utcnow()


class JSONEncoder(BaseJSONEncoder):
    def default(self, obj):
        if is_lazy_string(obj):
            obj = str(obj)
            return obj

        return JSONEncoder.default(self, obj)


class DummyDict(MutableMapping):
    @property
    def dct(self):
        return self.__dict__

    def __getitem__(self, key):
        try:
            return self.dct[key]
        except KeyError:
            return None

    def __setitem__(self, key, value):
        self.dct[key] = value

        return self[key]

    def __delitem__(self, key):
        try:
            del self.dct[key]
        except KeyError:
            pass

    def __iter__(self):
        return self.dct.__iter__()

    def __len__(self):
        return self.dct.__len__()