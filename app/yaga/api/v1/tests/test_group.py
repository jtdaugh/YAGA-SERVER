from __future__ import absolute_import, division, unicode_literals

from itertools import imap

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from . import GROUP_MEMBERS, GROUP_NAME, USER_PHONE_NUMBER, AuthMixin


class GroupTestCase(
    AuthMixin,
    APITestCase
):
    def setUp(self):  # noqa
        self.login()

    def test_empty_groups(self):
        response = self.client.get(
            reverse('yaga:api:v1:group:list-create')
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertIsInstance(
            response.data,
            list
        )
        self.assertFalse(
            response.data
        )

    def test_access_group(self):
        self.logout()

        response = self.client.get(
            reverse('yaga:api:v1:group:list-create')
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_create_group(self):
        response = self.client.post(
            reverse('yaga:api:v1:group:list-create'),
            {
                'name': GROUP_NAME
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertTrue(
            response.data
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
            GROUP_NAME
        )
        self.assertIn(
            'members',
            response.data
        )
        self.assertIn(
            'id',
            response.data
        )
        group_id = response.data['id']

        response = self.client.get(
            reverse('yaga:api:v1:group:retrieve-update', kwargs={
                'group_id': group_id
            })
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertIsInstance(
            response.data,
            dict
        )
        self.assertTrue(
            response.data
        )
        self.assertIn(
            'id',
            response.data
        )
        self.assertIn(
            'posts',
            response.data
        )
        self.assertFalse(
            response.data['posts']
        )
        self.assertIsInstance(
            response.data['posts'],
            list
        )
        self.assertIn(
            'members',
            response.data
        )
        self.assertIsInstance(
            response.data['members'],
            list
        )
        self.assertTrue(
            response.data['members']
        )
        self.assertIn(
            'mute',
            response.data['members'][0]
        )
        self.assertFalse(
            response.data['members'][0]['mute']
        )
        self.assertIn(
            'joined_at',
            response.data['members'][0]
        )
        self.assertIn(
            'user',
            response.data['members'][0]
        )
        self.assertTrue(
            response.data['members'][0]['user']
        )
        self.assertIn(
            'id',
            response.data['members'][0]['user']
        )
        self.assertIn(
            'name',
            response.data['members'][0]['user']
        )
        self.assertIsNone(
            response.data['members'][0]['user']['name']
        )
        self.assertIn(
            'phone',
            response.data['members'][0]['user']
        )
        self.assertEqual(
            USER_PHONE_NUMBER,
            response.data['members'][0]['user']['phone']
        )

    def test_add_group_member(self):
        response = self.client.post(
            reverse('yaga:api:v1:group:list-create'),
            {
                'name': GROUP_NAME
            }
        )
        group_id = response.data['id']

        response = self.client.put(
            reverse('yaga:api:v1:group:members:add', kwargs={
                'group_id': group_id
            }),
            {
                'phones': GROUP_MEMBERS
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertIsInstance(
            response.data,
            dict
        )
        self.assertTrue(
            response.data
        )
        self.assertIn(
            'id',
            response.data
        )
        self.assertIn(
            'members',
            response.data
        )
        self.assertIsInstance(
            response.data['members'],
            list
        )
        self.assertTrue(
            response.data['members']
        )
        self.assertEqual(
            len(response.data['members']),
            len(GROUP_MEMBERS) + 1
        )
        for member in response.data['members']:
            self.assertIsInstance(
                member,
                dict
            )
            self.assertIn(
                'joined_at',
                member
            )
            self.assertIn(
                'mute',
                member
            )
            self.assertFalse(
                member['mute']
            )
            self.assertIn(
                'user',
                member
            )
            self.assertTrue(
                member['user']
            )
            self.assertIn(
                'id',
                member['user']
            )
            self.assertIn(
                'name',
                member['user']
            )
            self.assertIsNone(
                member['user']['name']
            )
            self.assertIn(
                'phone',
                member['user']
            )
            self.assertIn(
                member['user']['phone'],
                GROUP_MEMBERS + [USER_PHONE_NUMBER]
            )

    def test_remove_group_member(self):
        response = self.client.post(
            reverse('yaga:api:v1:group:list-create'),
            {
                'name': GROUP_NAME
            }
        )
        group_id = response.data['id']

        response = self.client.put(
            reverse('yaga:api:v1:group:members:add', kwargs={
                'group_id': group_id
            }),
            {
                'phones': GROUP_MEMBERS
            }
        )

        for member in GROUP_MEMBERS:
            response = self.client.put(
                reverse('yaga:api:v1:group:members:remove', kwargs={
                    'group_id': group_id
                }),
                {
                    'phone': member
                }
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK
            )
            self.assertIsInstance(
                response.data,
                dict
            )
            self.assertTrue(
                response.data
            )
            self.assertIn(
                'id',
                response.data
            )
            self.assertIn(
                'members',
                response.data
            )
            self.assertIsInstance(
                response.data['members'],
                list
            )
            self.assertTrue(
                response.data['members']
            )
            self.assertNotIn(
                member,
                list(
                    imap(
                        lambda member: member['user']['phone'],
                        response.data['members']
                    )
                )
            )

        response = self.client.get(
            reverse('yaga:api:v1:group:retrieve-update', kwargs={
                'group_id': group_id
            })
        )
        self.assertEqual(
            len(response.data['members']),
            1
        )

        response = self.client.put(
            reverse('yaga:api:v1:group:members:remove', kwargs={
                'group_id': group_id
            }),
            {
                'phone': USER_PHONE_NUMBER
            }
        )

        response = self.client.get(
            reverse('yaga:api:v1:group:retrieve-update', kwargs={
                'group_id': group_id
            })
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        response = self.client.get(
            reverse('yaga:api:v1:group:list-create')
        )
        self.assertIsInstance(
            response.data,
            list
        )
        self.assertFalse(
            response.data
        )
