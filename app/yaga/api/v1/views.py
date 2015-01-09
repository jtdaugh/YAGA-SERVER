from __future__ import absolute_import, division, unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import (
    RetrieveAPIView, CreateAPIView, UpdateAPIView,
    RetrieveUpdateAPIView, ListCreateAPIView,
    DestroyAPIView, RetrieveUpdateDestroyAPIView,
    get_object_or_404
)
# from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    UserSerializer,
    CodeRetrieveSerializer, CodeCreateSerializer,
    TokenSerializer,
    GroupListSerializer, GroupRetrieveSerializer,
    GroupManageMemberAddSerializer, GroupManageMemberRemoveSerializer,
    MemberSerializer,
    SinceSerializer,
    PostSerializer
)
from ...models import Code, Group, Post, Member, Like
from .permissions import (
    TokenOwner, IsAnonymous, GroupMemeber, PostOwner, PostGroupMember
)
from .throttling import CodeScopedRateThrottle, TokenScopedRateThrottle


class UserRetrieveUpdateAPIView(
    RetrieveUpdateAPIView,
):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        obj = self.request.user

        self.check_object_permissions(self.request, obj)

        return obj


class CodeCreateAPIView(
    CreateAPIView
):
    model = Code
    serializer_class = CodeCreateSerializer
    throttle_classes = (CodeScopedRateThrottle,)
    permission_classes = (IsAnonymous,)

    @method_decorator(transaction.non_atomic_requests)
    def dispatch(self, *args, **kwargs):
        return super(CodeCreateAPIView, self).dispatch(*args, **kwargs)

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
    RetrieveAPIView
):
    serializer_class = CodeRetrieveSerializer
    permission_classes = (IsAnonymous,)

    def get_queryset(self):
        return Code.objects.all()

    def get(self, request):
        data = self.request.QUERY_PARAMS.dict()
        return self.retrieve(request, data)

    def post(self, request):
        data = request.data
        return self.retrieve(request, data)

    def retrieve(self, request, data):
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        queryset = self.filter_queryset(self.get_queryset())

        code = get_object_or_404(queryset, **serializer.data)

        self.check_object_permissions(self.request, code)

        return Response({
            'expire_at': code.expire_at
        })


class TokenCreateAPIView(
    CreateAPIView
):
    serializer_class = TokenSerializer
    permission_classes = (IsAnonymous,)
    throttle_classes = (TokenScopedRateThrottle,)

    @method_decorator(transaction.non_atomic_requests)
    def dispatch(self, *args, **kwargs):
        return super(TokenCreateAPIView, self).dispatch(*args, **kwargs)

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
    DestroyAPIView
):
    permission_classes = (IsAuthenticated, TokenOwner)

    def get_serializer_class(self):
        return None

    def get_object(self):
        obj = self.request.auth

        self.check_object_permissions(self.request, obj)

        return obj


class GroupListCreateAPIView(
    ListCreateAPIView
):
    permission_classes = (IsAuthenticated,)
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
    RetrieveUpdateAPIView
):
    lookup_url_kwarg = 'group_id'
    serializer_class = GroupRetrieveSerializer
    permission_classes = (IsAuthenticated, GroupMemeber)

    def get_queryset(self):
        post_filter = {
            'ready': True
        }

        serializer = SinceSerializer(data=self.request.QUERY_PARAMS.dict())

        if serializer.is_valid():
            post_filter['ready_at__gte'] = (
                serializer.validated_data['since']
                -
                settings.CONSTANTS.SLOP_FACTOR
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
                ).order_by('-ready_at'),
            )
        )

        return queryset


class GroupManageMemberAPIView(
    UpdateAPIView
):
    lookup_url_kwarg = 'group_id'
    permission_classes = (IsAuthenticated, GroupMemeber)

    def get_queryset(self):
        return Group.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        model = get_user_model()

        self.perform_action(instance, model, serializer.data)

        serializer = GroupListSerializer(instance)

        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )


class GroupManageMemberAddAPIView(
    GroupManageMemberAPIView
):
    serializer_class = GroupManageMemberAddSerializer

    def perform_action(self, instance, model, data):
        for phone in data['phones']:
            user = model.objects.get_or_create(
                phone=phone
            )

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
    CreateAPIView
):
    lookup_url_kwarg = 'group_id'
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, GroupMemeber)

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
    RetrieveUpdateDestroyAPIView
):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, PostOwner)

    def get_queryset(self):
        return Post.objects.all()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        obj = get_object_or_404(
            queryset,
            group__pk=self.kwargs['group_id'],
            pk=self.kwargs['post_id'],
        )

        self.check_object_permissions(self.request, obj)

        return obj

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.ready:
            self.perform_destroy(instance)

            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {
                    'ready': [_('Can not remove not ready post.')]
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class LikeCreateDestroyAPIView(
    CreateAPIView,
    DestroyAPIView
):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, PostGroupMember)

    def get_queryset(self):
        return Post.objects.all()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        obj = get_object_or_404(
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
