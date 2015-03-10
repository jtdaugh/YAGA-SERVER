from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.utils.translation import ugettext_lazy as _
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.views import NonAtomicView

from . import permissions, serializers, throttling
from ...conf import settings
from ...models import Code, Contact, Group, Like, Member, Post
from ...utils import patch_as_put


@patch_as_put
class UserRetrieveUpdateAPIView(
    generics.RetrieveUpdateAPIView,
):
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        permission_objects = super(
            UserRetrieveUpdateAPIView, self
        ).get_permissions()

        if self.request.method != 'GET':
            permission_objects.append(permissions.EmptyProfile())

        return permission_objects

    def get_object(self):
        obj = self.request.user

        self.check_object_permissions(self.request, obj)

        return obj

    def check_object_permissions(self, request, obj):
        return super(
            UserRetrieveUpdateAPIView, self
        ).check_object_permissions(request, obj)


class CodeCreateAPIView(
    NonAtomicView,
    generics.CreateAPIView
):
    serializer_class = serializers.CodeCreateSerializer
    throttle_classes = (throttling.CodeScopedRateThrottle,)
    permission_classes = (permissions.IsAnonymous,)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            code = Code()
            code.phone = serializer.validated_data['phone']

            if code.verify_phone():
                code.save()

                return Response(
                    {
                        'expire_at': code.expire_at
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {
                        'phone': [_('Can not to send verification code.')]
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                dict(serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )


class CodeRetrieveAPIView(
    generics.RetrieveAPIView
):
    serializer_class = serializers.CodeRetrieveSerializer
    permission_classes = (permissions.IsAnonymous,)

    def get_queryset(self):
        return Code.objects.all()

    def get(self, request, *args, **kwargs):
        data = self.request.QUERY_PARAMS.dict()
        return self.retrieve(request, data, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.data
        return self.retrieve(request, data, *args, **kwargs)

    def retrieve(self, request, data, *args, **kwargs):
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        queryset = self.filter_queryset(self.get_queryset())

        code = generics.get_object_or_404(
            queryset, **serializer.validated_data
        )

        self.check_object_permissions(self.request, code)

        return Response({
            'expire_at': code.expire_at
        })


class TokenCreateAPIView(
    NonAtomicView,
    generics.CreateAPIView
):
    serializer_class = serializers.TokenSerializer
    permission_classes = (permissions.IsAnonymous,)
    throttle_classes = (throttling.TokenScopedRateThrottle,)

    def get_object(self):
        obj = self.request.auth

        self.check_object_permissions(self.request, obj)

        return obj

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {
                'token': serializer.instance.key
            },
            status=status.HTTP_201_CREATED,
        )


class TokenDestroyAPIView(
    generics.DestroyAPIView
):
    permission_classes = (IsAuthenticated, permissions.TokenOwner)

    def get_serializer_class(self):
        return None

    def get_object(self):
        obj = self.request.auth

        self.check_object_permissions(self.request, obj)

        return obj


class GroupListCreateAPIView(
    generics.ListCreateAPIView
):
    permission_classes = (IsAuthenticated, permissions.FulfilledProfile)
    serializer_class = serializers.GroupListSerializer

    def get_queryset(self):
        return Group.objects.prefetch_related(
            Prefetch(
                'member_set',
                queryset=Member.objects.prefetch_related(
                    'user',
                )
            ),
        ).filter(
            members=self.request.user
        ).order_by(
            '-updated_at'
        )

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        obj = Member()
        obj.group = serializer.instance
        obj.user = request.user
        obj.creator = request.user
        obj.save()

        return Response(
            dict(serializer.data),
            status=status.HTTP_201_CREATED,
        )


@patch_as_put
class GroupRetrieveUpdateAPIView(
    generics.RetrieveUpdateAPIView
):
    lookup_url_kwarg = 'group_id'
    serializer_class = serializers.GroupRetrieveSerializer
    permission_classes = (
        IsAuthenticated, permissions.GroupMemeber, permissions.FulfilledProfile
    )

    def get_queryset(self):
        post_filter = {
            'ready': True
        }

        serializer = serializers.SinceSerializer(
            data=self.request.QUERY_PARAMS.dict()
        )

        if serializer.is_valid():
            post_filter['updated_at__gte'] = (
                serializer.validated_data['since']
                -
                settings.YAGA_SLOP_FACTOR
            )

        queryset = Group.objects.prefetch_related(
            Prefetch(
                'member_set',
                queryset=Member.objects.prefetch_related(
                    'user',
                )
            ),
            Prefetch(
                'post_set',
                queryset=Post.objects.prefetch_related(
                    Prefetch(
                        'user',
                    )
                ).filter(
                    **post_filter
                ).order_by('-updated_at'),
            )
        )

        return queryset


@patch_as_put
class GroupManageMemberAPIView(
    generics.UpdateAPIView
):
    lookup_url_kwarg = 'group_id'
    permission_classes = (
        IsAuthenticated, permissions.GroupMemeber, permissions.FulfilledProfile
    )

    def get_queryset(self):
        return Group.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        model = get_user_model()

        self.perform_action(instance, model, serializer.validated_data)

        serializer = serializers.GroupListSerializer(instance)

        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )


class GroupManageMemberAddAPIView(
    GroupManageMemberAPIView
):
    serializer_class = serializers.GroupManageMemberAddSerializer

    def perform_add(self, instance, user):
        if user.is_active:
            obj = instance.member_set.filter(
                group=instance,
                user=user
            ).first()

            if not obj:
                obj = Member()
                obj.group = instance
                obj.user = user
                obj.creator = self.request.user
                obj.save()

    def perform_action(self, instance, model, data):
        if data.get('names'):
            for name in data['names']:
                user = model.objects.filter(
                    name__iexact=name
                ).first()

                if user:
                    self.perform_add(instance, user)

        if data.get('phones'):
            for phone in data['phones']:
                user = model.objects.get_or_create(
                    phone=phone
                )

                self.perform_add(instance, user)


class GroupManageMemberRemoveAPIView(
    GroupManageMemberAPIView
):
    serializer_class = serializers.GroupManageMemberRemoveSerializer

    def perform_action(self, instance, model, data):
        user = model.objects.get_or_create(
            phone=data['phone']
        )

        obj = instance.member_set.filter(
            group=instance,
            user=user
        ).first()

        if obj:
            obj.bridge.deleter = self.request.user
            obj.delete()


class GroupManageMemberMuteAPIView(
    GroupManageMemberAPIView
):
    serializer_class = serializers.MemberSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        obj = instance.member_set.get(
            user=self.request.user
        )

        serializer = self.get_serializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        serializer = serializers.GroupListSerializer(instance)

        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )


class PostCreateAPIView(
    generics.CreateAPIView
):
    lookup_url_kwarg = 'group_id'
    serializer_class = serializers.PostSerializer
    permission_classes = (
        IsAuthenticated, permissions.GroupMemeber, permissions.FulfilledProfile
    )

    def get_queryset(self):
        return Group.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = self.get_object()

        obj = Post()
        obj.user = request.user
        obj.group = group
        if serializer.validated_data.get('name'):
            obj.name = serializer.validated_data['name']
        obj.save()

        serializer = self.get_serializer(obj)
        response = dict(serializer.data)

        response['meta'] = obj.sign_s3()

        return Response(
            response,
            status=status.HTTP_201_CREATED
        )


class PostAPIView(
    object
):
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        obj = generics.get_object_or_404(
            queryset,
            group__pk=self.kwargs['group_id'],
            pk=self.kwargs['post_id'],
        )

        self.check_object_permissions(self.request, obj)

        return obj


@patch_as_put
class PostRetrieveUpdateDestroyAPIView(
    PostAPIView,
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = serializers.PostSerializer
    permission_classes = (
        IsAuthenticated, permissions.PostOwnerOrGroupMember,
        permissions.AvailablePost, permissions.FulfilledProfile
    )

    def get_queryset(self):
        return Post.objects.all()

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.save()

    def get_object(self):
        instance = super(PostRetrieveUpdateDestroyAPIView, self).get_object()
        instance.bridge.updater = self.request.user

        return instance

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        self.perform_destroy(instance)

        serializer = self.get_serializer(instance)

        serializer = dict(serializer.data)

        serializer['attachment'] = None

        return Response(
            serializer,
            status=status.HTTP_200_OK
        )


class LikeCreateDestroyAPIView(
    PostAPIView,
    generics.CreateAPIView,
    generics.DestroyAPIView
):
    serializer_class = serializers.PostSerializer
    permission_classes = (
        IsAuthenticated, permissions.PostGroupMember,
        permissions.AvailablePost, permissions.FulfilledProfile
    )

    def get_queryset(self):
        return Post.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        obj = self.get_object().like_set.filter(
            user=request.user
        ).first()

        if obj:
            obj.delete()

        serializer = self.get_serializer(instance)

        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        instance = self.get_object()

        if not instance.like_set.filter(
            user=self.request.user
        ).exists():
            obj = Like()
            obj.user = self.request.user
            obj.post = instance
            obj.save()

        serializer = self.get_serializer(instance)

        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )


class DeviceCreateAPIView(
    generics.CreateAPIView
):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.DeviceSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ContactListCreateAPIView(
    generics.ListCreateAPIView
):
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAuthenticated,)
    throttle_classes = (throttling.UserSearchScopedRateThrottle,)

    def get_queryset(self):
        serializer = serializers.UserSearchSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        return get_user_model().objects.filter(
            verified=True,
            phone__in=serializer.validated_data['phones']
        )

    def post(self, request, *args, **kwargs):
        super(ContactListCreateAPIView, self).post(request, *args, **kwargs)

        return self.get(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = serializers.ContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

    def perform_create(self, serializer):
        Contact.objects.filter(
            user=self.request.user
        ).delete()

        serializer.save(user=self.request.user)
