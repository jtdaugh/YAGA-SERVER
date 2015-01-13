from __future__ import absolute_import, division, unicode_literals

from django.contrib.auth import get_user_model

from accounts.models import Token


PHONE_NUMBER = '+380632237710'
NAME = 'yaga_user'


class AuthMixin(
    object
):
    def setUp(self):
        model = get_user_model()
        user = model()
        user.phone = PHONE_NUMBER
        user.save()

        token = Token()
        token.user = user
        token.save()

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token.key
        )
