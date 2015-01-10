from __future__ import absolute_import, division, unicode_literals

from phonenumber_field.formfields import \
    PhoneNumberField as BasePhoneNumberField


class PhoneNumberField(
    BasePhoneNumberField
):
    def to_python(self, value):
        if not value.startswith('+'):
            value = '+' + value

        return super(PhoneNumberField, self).to_python(value)
