from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from . import USER_NAME, USER_PHONE_NUMBER, AuthMixin


class ProfileTestCase(
    AuthMixin,
    APITestCase
):
    def setUp(self):  # noqa
        self.login()

    def test_empty_profile(self):
        response = self.client.get(
            reverse('yaga:api:v1:user:profile')
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertIn(
            'id',
            response.data
        )
        self.assertIn(
            'phone',
            response.data
        )
        self.assertEqual(
            response.data['phone'],
            USER_PHONE_NUMBER
        )
        self.assertIn(
            'name',
            response.data
        )
        self.assertEqual(
            response.data['name'],
            None
        )

    def test_profile(self):
        response = self.client.put(
            reverse('yaga:api:v1:user:profile'),
            data={
                'name': USER_NAME
            }
        )
        self.assertIn(
            'id',
            response.data
        )
        self.assertIn(
            'name',
            response.data
        )
        self.assertEqual(
            response.data['name'],
            USER_NAME
        )
