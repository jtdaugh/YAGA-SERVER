from __future__ import absolute_import, division, unicode_literals

from flask import g

from .....validators import BaseValidator
from ...repository import user_storage


class CurrentTokenValidator(BaseValidator):
    CODE = 'unknown_token'

    def validate(self, form, field):
        if field.data != g.token:
            raise self.stop


class AvailablePhoneValidator(BaseValidator):
    CODE = 'phone_registered'

    def validate(self, form, field):
        obj = user_storage.get(
            phone=field.data
        )

        if obj:
            raise self.stop


# class AvailableNameValidator(BaseValidator):
#     CODE = 'name_registered'

#     def validate(self, form, field):
#         obj = user_storage.get(
#             name=field.data
#         )

#         if obj:
#             raise self.stop
