from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib.auth import get_user_model

from .models import Code


class CodeBackend(
    object
):
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    model = get_user_model()

    def authenticate(self, phone=None, code=None):
        if None is (phone, code):
            return None

        code_obj = Code.objects.filter(
            phone=phone,
        ).order_by('-expire_at').first()

        if code_obj is None:
            return None

        response = code_obj.check_code(code)

        if response.is_valid():
            code_obj.delete()

            user = self.model.objects.get_or_create(
                phone=phone
            )

            if not user.verified:
                user.verified = True
                user.save()

            return user

        # invalid code was many times
        elif response.exceeded():
            code_obj.delete()

    def get_user(self, user_id):
        try:
            return self.model.objects.get(
                pk=user_id
            )
        except self.model.DoesNotExist:
            pass
