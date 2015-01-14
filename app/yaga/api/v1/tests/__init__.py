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
    def get_user(self, phone=None):
        if phone is None:
            phone = USER_PHONE_NUMBER

        model = get_user_model()

        user = model.objects.get_or_create(
            phone=phone
        )

        return user

    def login(self, user=None):
        if user is None:
            user = self.get_user()

        token = Token()
        token.user = user
        token.save()

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token.key
        )

    def logout(self):
        self.client.credentials()
