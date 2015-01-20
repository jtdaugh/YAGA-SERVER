from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from . import (
    GROUP_MEMBERS, USER_NAME, USER_PHONE_NUMBER, USER_TOKEN, AuthMixin
)
from ....models import Device


class UserTestCase(
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
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
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

    def test_device(self):
        response = self.client.post(
            reverse('yaga:api:v1:user:device'),
            data={
                'vendor': 'IOS',
                'token': USER_TOKEN
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertIsInstance(
            response.data,
            dict
        )
        self.assertTrue(
            response.data
        )
        self.assertIn(
            'token',
            response.data
        )
        self.assertEqual(
            USER_TOKEN,
            response.data['token']
        )

        response = self.client.post(
            reverse('yaga:api:v1:user:device'),
            data={
                'vendor': 'IOS',
                'token': USER_TOKEN
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertIsInstance(
            response.data,
            dict
        )
        self.assertTrue(
            response.data
        )
        self.assertIn(
            'token',
            response.data
        )
        self.assertEqual(
            USER_TOKEN,
            response.data['token']
        )

        self.logout()

        user = self.get_user(GROUP_MEMBERS[1])

        self.login(user)

        response = self.client.post(
            reverse('yaga:api:v1:user:device'),
            data={
                'vendor': 'IOS',
                'token': USER_TOKEN
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertIsInstance(
            response.data,
            dict
        )
        self.assertTrue(
            response.data
        )
        self.assertIn(
            'token',
            response.data
        )
        self.assertEqual(
            USER_TOKEN,
            response.data['token']
        )
        device = Device.objects.get(
            token=USER_TOKEN
        )
        self.assertEqual(
            device.user,
            user
        )
