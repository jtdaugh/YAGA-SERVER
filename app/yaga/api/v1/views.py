from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.views import NonAtomicView

from ...conf import settings
from ...models import Code, Group, Like, Member, Post
from .permissions import (
    AvailablePost, GroupMemeber, IsAnonymous, PostGroupMember, PostOwner,
    TokenOwner, UserWithName
)
from .serializers import (
    CodeCreateSerializer, CodeRetrieveSerializer, DeviceSerializer,
    GroupListSerializer, GroupManageMemberAddSerializer,
    GroupManageMemberRemoveSerializer, GroupRetrieveSerializer,
    MemberSerializer, PostSerializer, SinceSerializer, TokenSerializer,
    UserSearchSerializer, UserSerializer
)
from .throttling import CodeScopedRateThrottle, TokenScopedRateThrottle


class UserRetrieveUpdateAPIView(
    generics.RetrieveUpdateAPIView,
):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        obj = self.request.user

        self.check_object_permissions(self.request, obj)

        return obj


class CodeCreateAPIView(
    NonAtomicView,
    generics.CreateAPIView
):
    model = Code
    serializer_class = CodeCreateSerializer
    throttle_classes = (CodeScopedRateThrottle,)
    permission_classes = (IsAnonymous,)

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
    serializer_class = CodeRetrieveSerializer
    permission_classes = (IsAnonymous,)

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
    serializer_class = TokenSerializer
    permission_classes = (IsAnonymous,)
    throttle_classes = (TokenScopedRateThrottle,)

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
    permission_classes = (IsAuthenticated, TokenOwner)

    def get_serializer_class(self):
        return None

    def get_object(self):
        obj = self.request.auth

        self.check_object_permissions(self.request, obj)

        return obj


class GroupListCreateAPIView(
    generics.ListCreateAPIView
):
    permission_classes = (IsAuthenticated, UserWithName)
    serializer_class = GroupListSerializer

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

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        obj = Member()
        obj.group = serializer.instance
        obj.user = request.user
        obj.save()

        return Response(
            dict(serializer.data),
            status=status.HTTP_201_CREATED,
        )


class GroupRetrieveUpdateAPIView(
    generics.RetrieveUpdateAPIView
):
    lookup_url_kwarg = 'group_id'
    serializer_class = GroupRetrieveSerializer
    permission_classes = (IsAuthenticated, GroupMemeber, UserWithName)

    def get_queryset(self):
        post_filter = {
            'ready': True
        }

        serializer = SinceSerializer(data=self.request.QUERY_PARAMS.dict())

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


class GroupManageMemberAPIView(
    generics.UpdateAPIView
):
    lookup_url_kwarg = 'group_id'
    permission_classes = (IsAuthenticated, GroupMemeber, UserWithName)

    def get_queryset(self):
        return Group.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # if not request.data.get('names'):
        #     request.data['names'] = []

        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        model = get_user_model()

        self.perform_action(instance, model, serializer.validated_data)

        serializer = GroupListSerializer(instance)

        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )


class GroupManageMemberAddAPIView(
    GroupManageMemberAPIView
):
    serializer_class = GroupManageMemberAddSerializer

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
                obj.save()

    def perform_action(self, instance, model, data):
        if data.get('names'):
            for name in data['names']:
                user = model.objects.filter(
                    name=name
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
    serializer_class = GroupManageMemberRemoveSerializer

    def perform_action(self, instance, model, data):
        user = model.objects.get_or_create(
            phone=data['phone']
        )

        obj = instance.member_set.filter(
            group=instance,
            user=user
        ).first()

        if obj:
            obj.delete()


class GroupManageMemberMuteAPIView(
    GroupManageMemberAPIView
):
    serializer_class = MemberSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        obj = instance.member_set.get(
            user=self.request.user
        )

        serializer = self.get_serializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        serializer = GroupListSerializer(instance)

        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )


class PostCreateAPIView(
    generics.CreateAPIView
):
    lookup_url_kwarg = 'group_id'
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, GroupMemeber, UserWithName)

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


class PostRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = PostSerializer
    permission_classes = (
        IsAuthenticated, PostOwner, AvailablePost, UserWithName
    )

    def get_queryset(self):
        return Post.objects.all()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        obj = generics.get_object_or_404(
            queryset,
            group__pk=self.kwargs['group_id'],
            pk=self.kwargs['post_id'],
        )

        self.check_object_permissions(self.request, obj)

        return obj

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.save()

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
    generics.CreateAPIView,
    generics.DestroyAPIView
):
    serializer_class = PostSerializer
    permission_classes = (
        IsAuthenticated, PostGroupMember, AvailablePost, UserWithName
    )

    def get_queryset(self):
        return Post.objects.all()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        obj = generics.get_object_or_404(
            queryset,
            group__pk=self.kwargs['group_id'],
            pk=self.kwargs['post_id'],
        )

        self.check_object_permissions(self.request, obj)

        return obj

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()

        instance = self.get_object().like_set.filter(
            user=request.user
        ).first()

        if instance:
            instance.delete()

        serializer = self.get_serializer(obj)

        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )

    def perform_create(self, serializer):
        if not serializer.instance.like_set.filter(
            user=self.request.user
        ).exists():
            obj = Like()
            obj.user = self.request.user
            obj.post = serializer.instance
            obj.save()


class LikeListAPIView(
    generics.ListAPIView,
):
    serializer_class = UserSerializer
    permission_classes = (
        IsAuthenticated, PostGroupMember, AvailablePost, UserWithName
    )

    def get_object(self):
        queryset = self.filter_queryset(self._get_queryset())

        obj = generics.get_object_or_404(
            queryset,
            group__pk=self.kwargs['group_id'],
            pk=self.kwargs['post_id'],
        )

        self.check_object_permissions(self.request, obj)

        return obj

    def _get_queryset(self):
        return Post.objects.all()

    def get_queryset(self):
        return (obj.user for obj in self.get_object().like_set.all())


class DeviceCreateAPIView(
    generics.CreateAPIView
):
    permission_classes = (IsAuthenticated,)
    serializer_class = DeviceSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserSearchListAPIView(
    generics.ListAPIView,
):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, UserWithName)

    def get_queryset(self):
        serializer = UserSearchSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        return get_user_model().objects.filter(
            verified=True,
            phone__in=serializer.validated_data['phones']
        )

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
