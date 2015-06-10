from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import uuid

from django.core.exceptions import ImproperlyConfigured
from django.db import connection, models
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible
from phonenumber_field.modelfields import \
    PhoneNumberField as BasePhoneNumberField
from rest_framework import serializers

from .conf import settings
from .form_fields import PhoneNumberField as FormPhoneNumberField
from .serializers import PhoneField

if settings.USE_FLANKER:
    from django_flanker.models import EmailField as BaseEmailField
else:
    from django.db.models import EmailField as BaseEmailField


@python_2_unicode_compatible
class UUIDRepresentation(
    uuid.UUID
):
    def __str__(self):
        if connection.vendor != 'postgresql':
            value = self.hex
        else:
            value = super(UUIDRepresentation, self).__str__()

        return str(value)

    def __len__(self):
        return len(self.__str__())


def uuid_representation(value):
    if not value:
        return None

    return UUIDRepresentation(str(value))


class UUIDField(
    six.with_metaclass(models.SubfieldBase, models.UUIDField)
):
    def __init__(self, *args, **kwargs):
        self.version = kwargs.pop('version', 4)
        self.auto = kwargs.pop('auto', True)

        self.node = kwargs.pop('node', None)
        self.clock_seq = kwargs.pop('clock_seq', None)
        self.namespace = kwargs.pop('namespace', None)
        self.uuid_name = kwargs.pop('uuid_name', None)

        if self.auto:
            self.empty_strings_allowed = False
            kwargs['blank'] = True
            kwargs.setdefault('editable', False)

        super(UUIDField, self).__init__(*args, **kwargs)

    def create_uuid(self):
        if self.version == 4:
            return uuid.uuid4()
        elif self.version == 1:
            return uuid.uuid1(self.node, self.clock_seq)
        elif self.version == 2:
            raise ImproperlyConfigured
        elif self.version == 3:
            return uuid.uuid3(self.namespace, self.uuid_name)
        elif self.version == 5:
            return uuid.uuid5(self.namespace, self.uuid_name)
        else:
            raise ImproperlyConfigured

    def set_default(self, model_instance):
        value = str(self.create_uuid())
        setattr(model_instance, self.attname, value)

        return value

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)

        if self.auto and add and value is None:
            value = self.set_default(model_instance)
        else:
            if self.auto and not value:
                value = self.set_default(model_instance)

        return value

    def get_prep_value(self, value):
        if isinstance(value, uuid.UUID):
            return value.hex
        if isinstance(value, six.string_types):
            return value.replace('-', '')

        return value

    def to_python(self, value):
        value = uuid_representation(value)

        return value

    def formfield(self, **kwargs):
        if self.auto:
            return None

        return super(UUIDField, self).formfield(**kwargs)


class PhoneNumberField(
    BasePhoneNumberField
):
    def formfield(self, **kwargs):
        defaults = {
            'form_class': FormPhoneNumberField,
        }
        defaults.update(kwargs)
        return super(PhoneNumberField, self).formfield(**defaults)


class EmailField(
    BaseEmailField
):
    pass


class BridgeStorage(
    object
):
    bridge = None


serializers.ModelSerializer.serializer_field_mapping[
    UUIDField
] = serializers.UUIDField
serializers.ModelSerializer.serializer_field_mapping[
    PhoneNumberField
] = PhoneField
