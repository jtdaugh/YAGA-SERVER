from __future__ import absolute_import, division, unicode_literals

from django.contrib.auth import get_user_model

from accounts.models import Token


USER_PHONE_NUMBER = '+380632237710'
USER_NAME = 'yaga_user'
GROUP_MEMBERS = ['+380919575676', '+380675093001', '+380938542758']
GROUP_NAME = 'yaga_group'


class AuthMixin(
    object
):
    def login(self):
        model = get_user_model()
        user = model.objects.get_or_create(
            phone=USER_PHONE_NUMBER
        )

        token = Token()
        token.user = user
        token.save()

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token.key
        )

    def logout(self):
        self.client.credentials()
