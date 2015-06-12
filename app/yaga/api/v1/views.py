from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import datetime

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from rest_framework import generics, status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.views import NonAtomicView, PatchAsPutMixin, SafeNonAtomicView

from . import permissions, serializers, throttling
from ... import notifications
from ...conf import settings
from ...models import (
    Code, Contact, Group, Like, Member, MonkeyUser, Post, PostCopy,
    post_attachment_preview_upload_to_trash, post_attachment_upload_to
)


class UserRetrieveUpdateAPIView(
    SafeNonAtomicView,
    PatchAsPutMixin,
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
        serializer = self.get_serializer(
            data=request.data
        )

        if serializer.is_valid():
            if settings.YAGA_MONKEY_LOGIN:
                monkey = MonkeyUser.objects.filter(
                    user__phone=serializer.validated_data['phone']
                ).first()

                if monkey:
                    serializer = serializers.AuthStatusResponseSerializer(
                        data={
                            'expire_at': datetime.datetime(
                                datetime.MAXYEAR, 12, 31
                            )
                        }
                    )

                    serializer.is_valid(raise_exception=True)

                    return Response(
                        dict(serializer.data),
                        status=status.HTTP_201_CREATED
                    )

            code = Code()
            code.phone = serializer.validated_data['phone']

            if code.verify_phone():
                code.save()

                serializer = serializers.AuthStatusResponseSerializer(
                    data={
                        'expire_at': code.expire_at
                    }
                )

                serializer.is_valid(raise_exception=True)

                return Response(
                    dict(serializer.data),
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
    NonAtomicView,
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
        serializer = self.get_serializer(
            data=data
        )
        serializer.is_valid(raise_exception=True)

        queryset = self.filter_queryset(self.get_queryset())

        code = generics.get_object_or_404(
            queryset, **serializer.validated_data
        )

        self.check_object_permissions(self.request, code)

        serializer = serializers.AuthStatusResponseSerializer(
            data={
                'expire_at': code.expire_at
            }
        )

        serializer.is_valid(raise_exception=True)

        return Response(
            dict(serializer.data)
        )


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
        serializer = self.get_serializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        serializer = serializers.TokenResponseSerializer(
            data={
                'token': serializer.instance.key
            }
        )

        serializer.is_valid(raise_exception=True)

        return Response(
            dict(serializer.data),
            status=status.HTTP_201_CREATED,
        )


class TokenDestroyAPIView(
    NonAtomicView,
    generics.DestroyAPIView
):
    permission_classes = (IsAuthenticated, permissions.TokenOwner)

    def get_serializer_class(self):
        return None

    def get_object(self):
        obj = self.request.auth

        self.check_object_permissions(self.request, obj)

        return obj


class GroupSearchListAPIView(
    NonAtomicView,
    generics.ListAPIView
):
    permission_classes = (IsAuthenticated, permissions.FulfilledProfile)
    serializer_class = serializers.GroupListSerializer

    def get_queryset(self):
        contact = Contact.objects.filter(user=self.request.user).first()

        if contact:
            phone_query = Q()

            for phone in contact.phones:
                phone_query |= Q(member__user__phone=phone)

            queryset = Group.objects.prefetch_related(
                Prefetch(
                    'member_set',
                    queryset=Member.objects.select_related('user')
                ),
            ).filter(
                Q(member__user__name__isnull=False) & phone_query
            ).exclude(
                members=self.request.user
            ).distinct()

            groups = list(queryset)

            groups.sort(
                key=lambda group: len(
                    set([
                        member.user.phone.as_e164
                        for member in group.member_set.all()
                    ])
                    &
                    set(contact.phones)
                ),
                reverse=True
            )
        else:
            groups = []

        return groups


class GroupListCreateAPIView(
    SafeNonAtomicView,
    generics.ListCreateAPIView
):
    permission_classes = (IsAuthenticated, permissions.FulfilledProfile)
    serializer_class = serializers.GroupListSerializer

    def get_throttles(self):
        if self.request.method != 'GET':
            return [throttling.GroupScopedRateThrottle()]
        else:
            return []

    def get_queryset(self):
        return Group.objects.prefetch_related(
            Prefetch(
                'member_set',
                queryset=Member.objects.select_related('user')
            ),
        ).filter(
            members=self.request.user
        ).order_by(
            '-updated_at'
        )

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def create(self, request):
        serializer = self.get_serializer(
            data=request.data
        )
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


class GroupRetrieveUpdateAPIView(
    SafeNonAtomicView,
    PatchAsPutMixin,
    generics.RetrieveUpdateAPIView
):
    lookup_url_kwarg = 'group_id'
    serializer_class = serializers.GroupRetrieveSerializer
    permission_classes = (
        IsAuthenticated, permissions.GroupMemeber, permissions.FulfilledProfile
    )

    def get_queryset(self):
        post_filter = {
            'state__in': (
                Post.state_choices.READY,
                Post.state_choices.DELETED
            )
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
                queryset=Member.objects.select_related('user')
            ),
            Prefetch(
                'post_set',
                queryset=Post.objects.select_related(
                    'user',
                    'namer'
                ).prefetch_related(
                    Prefetch(
                        'like_set',
                        queryset=Like.objects.select_related('user')
                    )
                ).filter(
                    **post_filter
                ).order_by('-ready_at'),
            )
        )

        return queryset

    def perform_update(self, serializer):
        if serializer.validated_data.get('name'):
            if (
                serializer.validated_data['name'] != serializer.instance.name
            ):
                notifications.RenameGroupNotification.schedule(
                    group=serializer.instance.pk,
                    emitter=self.request.user.pk,
                    old_name=serializer.instance.name,
                    new_name=serializer.validated_data['name']
                )

        super(
            GroupRetrieveUpdateAPIView, self
        ).perform_update(serializer)


class GroupMemberUpdateDestroyAPIView(
    PatchAsPutMixin,
    generics.UpdateAPIView,
    generics.DestroyAPIView
):
    throttle_classes = (throttling.MemberScopedRateThrottle,)
    lookup_url_kwarg = 'group_id'
    permission_classes = (
        IsAuthenticated, permissions.GroupMemeber, permissions.FulfilledProfile
    )

    serializer_class = serializers.GroupListSerializer

    def get_queryset(self):
        return Group.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = serializers.GroupManageMemberAddSerializer(
            data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        self.perform_update(instance, serializer.validated_data)

        serializer = serializers.GroupListSerializer(instance)

        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = serializers.GroupManageMemberRemoveSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        self.perform_destroy(instance, serializer.validated_data)

        serializer = serializers.GroupListSerializer(instance)

        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )

    def perform_update(self, instance, validated_data):
        query = None

        if validated_data.get('names'):
            name_filter = Q()
            for name in list(set(validated_data['names'])):
                name_filter |= Q(name__iexact=name)

            query = name_filter

        if validated_data.get('phones'):
            _query = Q(phone__in=list(set(validated_data['phones'])))

            if query:
                query |= _query
            else:
                query = _query

        if query:
            users = get_user_model().objects.filter(
                query
            )

            users = set(list(users))

            if validated_data.get('phones'):
                existing_phones = {user.phone.as_e164 for user in users}

                new_phones = set(validated_data['phones']) - existing_phones

                for phone in new_phones:
                    new_user = get_user_model().objects.get_or_create(
                        phone=phone
                    )

                    users.add(new_user)

            try:
                users.remove(self.request.user)
            except KeyError:
                pass

            existing_members = instance.member_set.filter(
                user__in=users
            )

            existing_users = {member.user for member in existing_members}

            new_users = users - existing_users

            new_active_users = [user for user in new_users if user.is_active]

            new_members = []

            for user in new_active_users:
                obj = Member()
                obj.group = instance
                obj.user = user
                obj.creator = self.request.user
                obj.save()

                new_members.append(obj)

                notifications.InviteDirectNotification.schedule(
                    group=obj.group.pk,
                    target=obj.user.pk,
                    emitter=obj.creator.pk
                )

            if new_members:
                notifications.MembersGroupNotification.schedule(
                    group=obj.group.pk,
                    targets=[member.user.pk for member in new_members],
                    emitter=obj.creator.pk
                )

    def perform_destroy(self, instance, validated_data):
        try:
            user = get_user_model().objects.get(
                phone=validated_data['phone']
            )

            obj = instance.member_set.get(
                user=user
            )

            is_muted_group = obj.mute

            obj.delete()

            if user != self.request.user:
                notifications.KickGroupNotification.schedule(
                    group=instance.pk,
                    target=user.pk,
                    emitter=self.request.user.pk
                )

                if not is_muted_group:
                    notifications.KickDirectNotification.schedule(
                        group=instance.pk,
                        target=user.pk,
                        emitter=self.request.user.pk
                    )
        except (get_user_model().DoesNotExist, Member.DoesNotExist):
            pass


class GroupMemberMuteAPIView(
    NonAtomicView,
    PatchAsPutMixin,
    generics.UpdateAPIView,
):
    lookup_url_kwarg = 'group_id'
    permission_classes = (
        IsAuthenticated, permissions.GroupMemeber, permissions.FulfilledProfile
    )

    serializer_class = serializers.MemberSerializer

    def get_queryset(self):
        return Group.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        obj = instance.member_set.get(
            user=self.request.user
        )

        serializer = self.get_serializer(
            obj,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        serializer = serializers.GroupListSerializer(instance)

        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )


class PostCreateAPIView(
    NonAtomicView,
    generics.CreateAPIView
):
    throttle_classes = (throttling.PostScopedRateThrottle,)
    lookup_url_kwarg = 'group_id'
    serializer_class = serializers.PostSerializer
    permission_classes = (
        IsAuthenticated, permissions.GroupMemeber, permissions.FulfilledProfile
    )

    def get_queryset(self):
        return Group.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        group = self.get_object()

        obj = Post()
        obj.user = request.user
        obj.group = group
        obj.owner = request.user
        if serializer.validated_data.get('name'):
            obj.name = serializer.validated_data['name']
            obj.namer = request.user
        obj.save()

        serializer = self.get_serializer(obj)
        response = dict(serializer.data)

        response['meta'] = {
            'attachment': obj.sign_s3(
                settings.YAGA_AWS_UPLOAD_MIME,
                post_attachment_upload_to
            ),
            'attachment_preview': obj.sign_s3(
                'application/octet-stream',
                post_attachment_preview_upload_to_trash
            )
        }

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


class PostRetrieveUpdateDestroyAPIView(
    SafeNonAtomicView,
    PostAPIView,
    PatchAsPutMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = serializers.PostSerializer
    permission_classes = (
        IsAuthenticated, permissions.PostOwnerOrPostGroupMember,
        permissions.AvailablePost, permissions.FulfilledProfile
    )

    def get_throttles(self):
        if self.request.method not in ('GET', 'DELETE'):
            return [throttling.PostScopedRateThrottle()]
        else:
            return []

    def get_queryset(self):
        return Post.objects.select_related(
            'user',
            'namer'
        ).prefetch_related(
            Prefetch(
                'like_set',
                queryset=Like.objects.select_related('user')
            )
        )

    def perform_update(self, serializer):
        if serializer.validated_data.get('name'):
            serializer.validated_data['namer'] = self.request.user

            if (
                (
                    serializer.validated_data['name']
                    !=
                    serializer.instance.name
                    or
                    serializer.instance.namer
                    !=
                    self.request.user
                )
                and
                serializer.instance.user != self.request.user
            ):
                notifications.CaptionDirectNotification.schedule(
                    post=serializer.instance.pk,
                    emitter=self.request.user.pk
                )

        super(
            PostRetrieveUpdateDestroyAPIView, self
        ).perform_update(serializer)

    def perform_destroy(self, instance):
        instance.mark_deleted()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        self.perform_destroy(instance)

        serializer = self.get_serializer(instance)

        response = dict(serializer.data)

        # files actually queued for delete
        response['attachment'] = None
        response['attachment_preview'] = None

        return Response(
            response,
            status=status.HTTP_200_OK
        )


class PostCopyUpdateAPIView(
    PostAPIView,
    PatchAsPutMixin,
    generics.UpdateAPIView
):
    throttle_classes = (throttling.PostScopedRateThrottle,)
    serializer_class = serializers.PostCopySerializer
    permission_classes = (
        IsAuthenticated, permissions.PostGroupMember,
        permissions.AvailablePost, permissions.FulfilledProfile
    )

    def get_queryset(self):
        return Post.objects.all()

    def put(self, request, *args, **kwargs):
        if request.method == 'PUT':
            raise MethodNotAllowed(request.method)

        return super(
            PostCopyUpdateAPIView, self
        ).put(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        posts = self.perform_copy(serializer)

        if posts:
            action_status = status.HTTP_201_CREATED
        else:
            action_status = status.HTTP_200_OK

        serializer = self.get_serializer(
            data={
                'groups': [post.group.pk for post in posts]
            }
        )

        serializer.is_valid(raise_exception=True)

        response = dict(serializer.data)

        return Response(
            response,
            status=action_status
        )

    def perform_copy(self, serializer):
        posts = []

        if serializer.validated_data.get('groups'):
            copied_groups = PostCopy.objects.filter(
                parent=serializer.instance
            ).values_list('group', flat=True)

            groups = Group.objects.filter(
                pk__in=serializer.validated_data['groups'],
                members=self.request.user
            ).exclude(
                pk__in=copied_groups
            ).exclude(
                pk=serializer.instance.group.pk
            )

            if groups:
                parent = serializer.instance

            for group in groups:
                copy = PostCopy()
                copy.parent = parent
                copy.group = group

                post = Post()
                post.state = Post.state_choices.PENDING
                post.user = self.request.user
                post.group = group

                for attr in PostCopy.copy_attrs:
                    setattr(post, attr, getattr(parent, attr))

                post.save()

                copy.post = post

                try:
                    copy.save()

                    posts.append(post)
                except IntegrityError:
                    post.delete()
                    continue

                if copy.parent.state == Post.state_choices.READY:
                    copy.schedule()

        return posts


class LikeCreateDestroyAPIView(
    NonAtomicView,
    PostAPIView,
    generics.CreateAPIView,
    generics.DestroyAPIView
):
    throttle_classes = (throttling.LikeScopedRateThrottle,)
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

            if obj.user != obj.post.user:
                notifications.LikeDirectNotification.schedule(
                    post=obj.post.pk,
                    emitter=obj.user.pk
                )

        serializer = self.get_serializer(instance)

        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )


class DeviceCreateAPIView(
    NonAtomicView,
    generics.CreateAPIView
):
    throttle_classes = (throttling.DeviceScopedRateThrottle,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.DeviceSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ContactListCreateAPIView(
    NonAtomicView,
    generics.ListCreateAPIView
):
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAuthenticated,)
    throttle_classes = (throttling.UserSearchScopedRateThrottle,)

    def get_queryset(self):
        serializer = serializers.UserSearchSerializer(
            data=self.request.data
        )
        serializer.is_valid(raise_exception=True)

        return get_user_model().objects.filter(
            verified=True,
            phone__in=list(set(serializer.validated_data['phones']))
        ).exclude(
            pk=self.request.user.pk
        ).exclude(
            name__isnull=True
        )

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            raise MethodNotAllowed(request.method)

        return super(
            ContactListCreateAPIView, self
        ).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)

        return self.get(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = serializers.ContactSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

    def perform_create(self, serializer):
        contact = Contact.objects.filter(
            user=self.request.user
        ).first()

        if contact:
            serializer.instance = contact

        serializer.save(user=self.request.user)
