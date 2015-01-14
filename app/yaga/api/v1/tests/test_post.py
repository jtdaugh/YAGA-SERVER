from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from uuid import UUID

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from . import GROUP_MEMBERS, GROUP_NAME, POST_NAME, AuthMixin
from ....models import Post


class GroupTestCase(
    AuthMixin,
    APITestCase
):
    def setUp(self):  # noqa
        self.login()

    def test_create_post(self):
        response = self.client.post(
            reverse('yaga:api:v1:groups:list-create'),
            {
                'name': GROUP_NAME
            }
        )
        group_id = response.data['id']

        response = self.client.post(
            reverse('yaga:api:v1:groups:posts:create', kwargs={
                'group_id': group_id
            }),
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
            'id',
            response.data
        )
        self.assertIn(
            'name',
            response.data
        )
        self.assertEqual(
            response.data['name'],
            None
        )
        self.assertIn(
            'meta',
            response.data
        )
        self.assertIsInstance(
            response.data['meta'],
            dict
        )
        self.assertTrue(
            response.data['meta']
        )

    def test_not_ready_post(self):
        response = self.client.post(
            reverse('yaga:api:v1:groups:list-create'),
            {
                'name': GROUP_NAME
            }
        )
        group_id = response.data['id']

        response = self.client.post(
            reverse('yaga:api:v1:groups:posts:create', kwargs={
                'group_id': group_id
            }),
        )
        post_id = response.data['id']

        response = self.client.get(
            reverse('yaga:api:v1:groups:posts:detail', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        response = self.client.put(
            reverse('yaga:api:v1:groups:posts:detail', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        response = self.client.delete(
            reverse('yaga:api:v1:groups:posts:detail', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_rename_post(self):
        response = self.client.post(
            reverse('yaga:api:v1:groups:list-create'),
            {
                'name': GROUP_NAME
            }
        )
        group_id = response.data['id']

        response = self.client.post(
            reverse('yaga:api:v1:groups:posts:create', kwargs={
                'group_id': group_id
            }),
        )
        post_id = response.data['id']

        post = Post.objects.get(
            pk=UUID(post_id)
        )
        post.ready = True
        post.save()

        response = self.client.get(
            reverse('yaga:api:v1:groups:posts:detail', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
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
            'name',
            response.data
        )
        self.assertEqual(
            response.data['name'],
            None
        )
        self.assertNotIn(
            'meta',
            response.data
        )

        response = self.client.put(
            reverse('yaga:api:v1:groups:posts:detail', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
            {
                'name': POST_NAME
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
            'name',
            response.data
        )
        self.assertEqual(
            response.data['name'],
            POST_NAME
        )

        response = self.client.get(
            reverse('yaga:api:v1:groups:posts:detail', kwargs={
                'group_id': group_id,
                'post_id': post_id
            })
        )
        self.assertEqual(
            response.data['name'],
            POST_NAME
        )

        response = self.client.put(
            reverse('yaga:api:v1:groups:members:add', kwargs={
                'group_id': group_id
            }),
            {
                'phones': [GROUP_MEMBERS[1]]
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.logout()

        user = self.get_user(GROUP_MEMBERS[1])

        self.login(user)

        response = self.client.get(
            reverse('yaga:api:v1:groups:posts:detail', kwargs={
                'group_id': group_id,
                'post_id': post_id
            })
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_destroy_post(self):
        response = self.client.post(
            reverse('yaga:api:v1:groups:list-create'),
            {
                'name': GROUP_NAME
            }
        )
        group_id = response.data['id']

        response = self.client.post(
            reverse('yaga:api:v1:groups:posts:create', kwargs={
                'group_id': group_id
            }),
        )
        post_id = response.data['id']

        response = self.client.delete(
            reverse('yaga:api:v1:groups:posts:detail', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        post = Post.objects.get(
            pk=UUID(post_id)
        )
        post.ready = True
        post.save()

        response = self.client.delete(
            reverse('yaga:api:v1:groups:posts:detail', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        response = self.client.delete(
            reverse('yaga:api:v1:groups:posts:detail', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_like_post(self):
        response = self.client.post(
            reverse('yaga:api:v1:groups:list-create'),
            {
                'name': GROUP_NAME
            }
        )
        group_id = response.data['id']

        response = self.client.post(
            reverse('yaga:api:v1:groups:posts:create', kwargs={
                'group_id': group_id
            }),
        )
        post_id = response.data['id']

        response = self.client.post(
            reverse('yaga:api:v1:groups:posts:like', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        response = self.client.delete(
            reverse('yaga:api:v1:groups:posts:like', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        post = Post.objects.get(
            pk=UUID(post_id)
        )
        post.ready = True
        post.save()

        response = self.client.get(
            reverse('yaga:api:v1:groups:posts:detail', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertIn(
            'likes',
            response.data
        )
        self.assertIsInstance(
            response.data['likes'],
            int
        )
        self.assertEqual(
            response.data['likes'],
            0
        )

        response = self.client.post(
            reverse('yaga:api:v1:groups:posts:like', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        response = self.client.get(
            reverse('yaga:api:v1:groups:posts:detail', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertIn(
            'likes',
            response.data
        )
        self.assertEqual(
            response.data['likes'],
            1
        )

        response = self.client.post(
            reverse('yaga:api:v1:groups:posts:like', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        response = self.client.get(
            reverse('yaga:api:v1:groups:posts:detail', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertIn(
            'likes',
            response.data
        )
        self.assertEqual(
            response.data['likes'],
            1
        )

        response = self.client.delete(
            reverse('yaga:api:v1:groups:posts:like', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        response = self.client.get(
            reverse('yaga:api:v1:groups:posts:detail', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertIn(
            'likes',
            response.data
        )
        self.assertEqual(
            response.data['likes'],
            0
        )

        response = self.client.delete(
            reverse('yaga:api:v1:groups:posts:like', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        response = self.client.get(
            reverse('yaga:api:v1:groups:posts:detail', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertIn(
            'likes',
            response.data
        )
        self.assertEqual(
            response.data['likes'],
            0
        )

        response = self.client.put(
            reverse('yaga:api:v1:groups:members:add', kwargs={
                'group_id': group_id
            }),
            {
                'phones': [GROUP_MEMBERS[1]]
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.logout()

        user = self.get_user(GROUP_MEMBERS[1])

        self.login(user)

        response = self.client.post(
            reverse('yaga:api:v1:groups:posts:like', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.logout()

        self.login()

        response = self.client.get(
            reverse('yaga:api:v1:groups:posts:detail', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertIn(
            'likes',
            response.data
        )
        self.assertEqual(
            response.data['likes'],
            1
        )

    def test_permission_post(self):
        response = self.client.post(
            reverse('yaga:api:v1:groups:list-create'),
            {
                'name': GROUP_NAME
            }
        )
        group_id = response.data['id']

        response = self.client.post(
            reverse('yaga:api:v1:groups:posts:create', kwargs={
                'group_id': group_id
            }),
        )
        post_id = response.data['id']

        self.logout()

        user = self.get_user(GROUP_MEMBERS[1])

        self.login(user)

        response = self.client.get(
            reverse('yaga:api:v1:groups:posts:detail', kwargs={
                'group_id': group_id,
                'post_id': post_id
            }),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )
