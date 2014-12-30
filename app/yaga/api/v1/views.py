from __future__ import absolute_import, division, unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import (
    RetrieveAPIView, CreateAPIView, UpdateAPIView,
    RetrieveUpdateAPIView, ListCreateAPIView,
    DestroyAPIView,
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
    PostCreateSerializer, PostRetrieveSerializer
)
from ...models import Code, Group, Post, Member
from .permissions import CanDestroyToken


class UserRetrieveUpdateAPIView(
    RetrieveUpdateAPIView,
):
    def get_object(self):
        return self.request.user

    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer


class CodeCreateAPIView(
    CreateAPIView
):
    model = Code
    serializer_class = CodeCreateSerializer

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


class TokenCreateDestroyAPIView(
    CreateAPIView,
    DestroyAPIView
):
    serializer_class = TokenSerializer
    permission_classes = (CanDestroyToken, )

    def get_object(self):
        return self.request.auth

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

        member = Member()
        member.group = serializer.instance
        member.user = request.user
        member.save()

        return Response(
            dict(serializer.data),
            status=status.HTTP_201_CREATED,
        )


class GroupRetrieveUpdateAPIView(
    RetrieveUpdateAPIView
):
    lookup_url_kwarg = 'group_id'
    serializer_class = GroupRetrieveSerializer
    permission_classes = (IsAuthenticated,)

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
        ).filter(
            members=self.request.user
        )

        return queryset


class GroupManageMemberAPIView(
    UpdateAPIView
):
    lookup_url_kwarg = 'group_id'
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Group.objects.filter(
            members=self.request.user
        )

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
                member = instance.member_set.filter(
                    group=instance,
                    user=user
                ).first()

                if not member:
                    member = Member()
                    member.group = instance
                    member.user = user
                    member.save()


class GroupManageMemberRemoveAPIView(
    GroupManageMemberAPIView
):
    serializer_class = GroupManageMemberRemoveSerializer

    def perform_action(self, instance, model, data):
        user = model.objects.get_or_create(
            phone=data['phone']
        )

        member = instance.member_set.filter(
            group=instance,
            user=user
        ).first()

        if member:
            member.delete()


class GroupManageMemberMuteAPIView(
    GroupManageMemberAPIView
):
    serializer_class = MemberSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        member = instance.member_set.get(
            user=self.request.user
        )

        serializer = self.get_serializer(member, data=request.data)
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
    serializer_class = PostCreateSerializer

    def get_queryset(self):
        return Group.objects.filter(
            members=self.request.user
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = self.get_object()

        post = Post()
        post.user = request.user
        post.group = group
        post.save()

        serializer = self.get_serializer(post)
        response = dict(serializer.data)

        response['meta'] = post.sign_s3()

        return Response(
            response,
            status=status.HTTP_201_CREATED
        )


class PostDestroyAPIView(
    DestroyAPIView
):
    serializer_class = PostRetrieveSerializer

    def get_object(self):
        queryset = Post.objects.exclude(
            ready_at=None
        )

        return get_object_or_404(
            queryset,
            user=self.request.user,
            group__pk=self.kwargs['group_id'],
            pk=self.kwargs['post_id'],
        )
