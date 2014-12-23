from __future__ import absolute_import, division, unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import (
    RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView,
    get_object_or_404
)
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    UserRetrieveSerializer, UserUpdateSerializer,
    CodeRetrieveSerializer, CodeCreateSerializer,
    TokenSerializer,
    GroupRetrieveSerializer, GroupCreateSerializer, GroupInviteSerializer
)
from ...models import Code, Group


class UserApiView(
    object
):
    def get_object(self):
        return self.request.user


class UserRetrieveAPIView(
    UserApiView,
    RetrieveAPIView,
):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserRetrieveSerializer


class UserUpdateAPIView(
    UserApiView,
    UpdateAPIView,
):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserUpdateSerializer


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
                serializer.errors,
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


class TokenCreateAPIView(
    CreateAPIView
):
    serializer_class = TokenSerializer

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


class GroupAPIview(
    object
):
    def get_queryset(self):
        return Group.objects.filter(
            members=self.request.user
        )


class GroupListAPIView(
    GroupAPIview,
    ListAPIView
):
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupRetrieveSerializer


class GroupRetrieveUpdateAPIView(
    GroupAPIview,
    UpdateAPIView,
    RetrieveAPIView
):
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupRetrieveSerializer

    def get_queryset(self):
        return Group.objects.filter(
            members=self.request.user
        )


class GroupCreateAPIView(
    CreateAPIView
):
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupCreateSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        serializer.instance.members.add(request.user)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class GroupAddUpdateAPIView(
    GroupAPIview,
    UpdateAPIView
):
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupInviteSerializer
    action = 'add'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        model = get_user_model()

        user = model.objects.get_or_create(
            phone=serializer.data['phone']
        )

        if user.is_active:
            getattr(instance.members, self.action)(user)
        else:
            return Response(
                {
                    'phone': [_('User account is disabled.')]
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = GroupRetrieveSerializer(instance)

        return Response(
            dict(serializer.data),
            status=status.HTTP_201_CREATED
        )


class GroupDeleteUpdateAPIView(
    GroupAddUpdateAPIView
):
    action = 'remove'
