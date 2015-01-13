from __future__ import absolute_import, division, unicode_literals

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase


from . import PHONE_NUMBER, NAME, AuthMixin


class ProfileTestCase(
    AuthMixin,
    APITestCase
):
    def test_empty_profile(self):
        response = self.client.get(
            reverse('yaga:api:v1:user:profile')
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertIn(
            'phone',
            response.data
        )
        self.assertIn(
            'name',
            response.data
        )
        self.assertIn(
            'phone',
            response.data
        )
        self.assertEqual(
            response.data['phone'],
            PHONE_NUMBER
        )
        self.assertEqual(
            response.data['name'],
            None
        )

    def test_profile(self):
        response = self.client.put(
            reverse('yaga:api:v1:user:profile'),
            data={
                'name': NAME
            }
        )
        self.assertIn(
            'name',
            response.data
        )
        self.assertEqual(
            response.data['name'],
            NAME
        )
