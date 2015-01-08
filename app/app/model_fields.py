from __future__ import absolute_import, division, unicode_literals

import uuid

from django.db import connection
from django.conf import settings
from django.utils import six
from django.db.models import SubfieldBase
from django.utils.encoding import python_2_unicode_compatible
if connection.vendor == 'postgresql':
    import psycopg2.extras
    psycopg2.extras.register_uuid()
    from django_extensions.db.fields import (
        PostgreSQLUUIDField as BaseUUIDField
    )
else:
    from django_extensions.db.fields import UUIDField as BaseUUIDField
from phonenumber_field.modelfields import (
    PhoneNumberField as BasePhoneNumberField
)

from app.form_fields import PhoneNumberField as FormPhoneNumberField
from app.utils import smart_text


if settings.UUID_HYPHENATE:
    @python_2_unicode_compatible
    class UUIDRepresentation(uuid.UUID):
        def __str__(self):
            return self.hex

        def __len__(self):
            return len(self.__str__())

    def uuid_representation(value):
        if not value:
            return None

        return UUIDRepresentation(smart_text(value))

    class UUIDField(six.with_metaclass(SubfieldBase, BaseUUIDField)):
        def to_python(self, value):
            return uuid_representation(value)
else:
    class UUIDField(BaseUUIDField):
        pass


class PhoneNumberField(
    BasePhoneNumberField
):
    def formfield(self, **kwargs):
        defaults = {
            'form_class': FormPhoneNumberField,
        }
        defaults.update(kwargs)
        return super(PhoneNumberField, self).formfield(**defaults)
