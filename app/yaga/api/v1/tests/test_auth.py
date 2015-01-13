from __future__ import absolute_import, division, unicode_literals

import json
import datetime

import responses
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ....models import Code
from . import PHONE_NUMBER


class AuthTestCase(
    APITestCase
):
    def test_non_authenticated(self):
        response = self.client.get(
            reverse('yaga:api:v1:user:profile')
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_invalid_phone(self):
        response = self.client.post(
            reverse('yaga:api:v1:auth:request'),
            {
                'phone': PHONE_NUMBER[2:]
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    @responses.activate
    def test_auth(self):
        valid_nexmo_response = {
            'status': '0',
            'request_id': 'nexmo_reques_id'
        }
        responses.add(
            responses.GET,
            Code.provider.SEND_VERIFY_ENDPOINT,
            body=json.dumps(valid_nexmo_response), status=200,
            content_type='application/json'
        )
        response = self.client.post(
            reverse('yaga:api:v1:auth:request'),
            {
                'phone': PHONE_NUMBER
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertIn(
            'expire_at',
            response.data
        )
        self.assertIsInstance(
            response.data['expire_at'], datetime.datetime
        )

        response = self.client.post(
            reverse('yaga:api:v1:auth:obtain'),
            {
                'phone': PHONE_NUMBER
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        valid_nexmo_response = {
            'status': '0',
            'event_id': '00000000',
            'price': '0.00000000',
            'currency': 'EUR',
            'request_id': 'nexmo_reques_id'
        }
        responses.add(
            responses.GET,
            Code.provider.CHECK_VERIFY_ENDPOINT,
            body=json.dumps(valid_nexmo_response), status=200,
            content_type='application/json'
        )
        response = self.client.post(
            reverse('yaga:api:v1:auth:obtain'),
            {
                'phone': PHONE_NUMBER,
                'code': '0000'
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertIn(
            'token',
            response.data
        )

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + response.data['token']
        )

        response = self.client.get(
            reverse('yaga:api:v1:user:profile')
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
