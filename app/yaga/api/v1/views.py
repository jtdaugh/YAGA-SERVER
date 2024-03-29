from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import datetime

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Q, Prefetch
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from itertools import chain
from rest_framework import generics, status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param

from app.views import NonAtomicView, PatchAsPutMixin, SafeNonAtomicView

from . import permissions, serializers, throttling
from ... import notifications
from ...conf import settings
from ...models import (
    Code, Contact, Group, Like, Member, MonkeyUser, Post, PostCopy,
    post_attachment_preview_upload_to_trash, post_attachment_upload_to
)
from ...utils import jsonp_renderer


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
        data = self.request.query_params.dict()
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


class GroupDiscoverListAPIView(
    NonAtomicView,
    generics.ListAPIView
):
    permission_classes = (IsAuthenticated, permissions.FulfilledProfile)
    serializer_class = serializers.GroupListSerializer

    def get_queryset(self):
        contact = Contact.objects.filter(user=self.request.user).first()

        phones = []

        if contact and contact.phones:
            for phone in contact.phones:
                phones.append(phone)

        for contact in Contact.objects.select_related(
            'user'
        ).filter(
            phones__contains=[self.request.user.phone.as_e164],
        ):
            phones.append(contact.user.phone.as_e164)

        phones = list(set(phones))

        query = Q(
            member__user=self.request.user,
            member__status__in=[
                Member.status_choices.LEFT,
                Member.status_choices.PENDING,
            ]
        )

        query |= Q(
            private=False,
            featured=True,
        )

        if phones:
            query |= Q(
                member__user__phone__in=phones,
                member__status__in=[
                    Member.status_choices.MEMBER,
                    Member.status_choices.FOLLOWER,
                ]
            )

        queryset = Group.objects.select_related(
            'creator'
        ).prefetch_related(
            Prefetch(
                'member_set',
                queryset=Member.objects.select_related('user').exclude(
                    status=Member.status_choices.LEFT
                )
            ),
        ).filter(
            query
        ).filter(
            updated_at__gte=(
                timezone.now()
                -
                settings.YAGA_GROUP_DISCOVER_THRESHOLD
            )
        ).exclude(
            pk__in=Group.objects.filter(
                member__user=self.request.user,
                member__status__in=[
                    Member.status_choices.MEMBER,
                    Member.status_choices.FOLLOWER
                ]
            )
        )

        if (
            self.request.bridge.yaga.CLIENT_VERSION
            <
            settings.YAGA_THIRD_RELEASE_CLIENT_VERSION
        ):
            queryset = queryset.filter(
                private=True
            )

        queryset = queryset.distinct()[:settings.YAGA_DISCOVER_LIMIT]


        groups = []
        # Don't return groups with <= 2 members
        for group in list(queryset):
            if (group.active_member_count() > 2):
                groups.append(group)

        if phones:
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
            groups.sort(
                key=lambda group: group.post_set.count(),
                reverse=True
            )

        groups.sort(
            key=lambda group: group.featured,
            reverse=True
        )

        return groups


class GroupSearchListAPIView(
    NonAtomicView,
    generics.ListAPIView
):
    permission_classes = (IsAuthenticated, permissions.FulfilledProfile)
    serializer_class = serializers.GroupListSerializer

    def get_queryset(self):
        serializer = serializers.GroupSearchSerializer(
            data=self.request.query_params.dict()
        )

        serializer.is_valid(raise_exception=True)

        return Group.objects.select_related(
            'creator'
        ).prefetch_related(
            Prefetch(
                'member_set',
                queryset=Member.objects.select_related('user').exclude(
                    status=Member.status_choices.LEFT
                )
            )
        ).filter(
            name__icontains=serializer.validated_data['name']
        ).exclude(
            pk__in=Group.objects.filter(
                member__user=self.request.user,
                member__status__in=[
                    Member.status_choices.MEMBER,
                    Member.status_choices.FOLLOWER
                ]
            )
        )


class PublicGroupListAPIView(
    NonAtomicView,
    generics.ListAPIView
):
    permission_classes = (IsAuthenticated, permissions.FulfilledProfile)
    serializer_class = serializers.PublicGroupListSerializer
    throttle_classes = (throttling.GroupScopedRateThrottle,)

    def get_queryset(self):
        return Group.objects.filter(
            private=False
        ).order_by(
            'created_at'
        )[:1]  # Yeah evil hardcode, cuz humanity is just first created ;)


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
                queryset=Member.objects.select_related('user').exclude(
                    status=Member.status_choices.LEFT
                )
            ),
        ).filter(
            member__user=self.request.user,
            member__status__in=[
                Member.status_choices.MEMBER,
            ]
        ).order_by(
            '-updated_at'
        )

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def create(self, request):
        serializer = self.get_serializer(
            data=request.data
        )
        if serializer.is_valid():
            self.perform_create(serializer)

            obj = Member()
            obj.group = serializer.instance
            obj.user = request.user
            obj.creator = request.user
            obj.status = Member.status_choices.MEMBER
            obj.save()

            return Response(
                dict(serializer.data),
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                dict(serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )


class PublicGroupGroupRetrieveAPIView(
    NonAtomicView,
    generics.RetrieveAPIView
):
    lookup_url_kwarg = 'group_id'
    serializer_class = serializers.PublicGroupRetrieveSerializer
    permission_classes = (permissions.PublicGroup, )
    renderer_classes = jsonp_renderer

    def get_queryset(self):
        return Group.objects.prefetch_related(
            Prefetch(
                'post_set',
                queryset=Post.objects.select_related(
                    'user',
                ).filter(
                    approval=Post.approval_choices.APPROVED,
                    state=Post.state_choices.READY
                ).order_by('-ready_at')
            )
        )


class SinceMixin(
    object
):
    lookup_url_kwarg = 'group_id'
    serializer_class = serializers.PostSerializer
    permission_classes = (
        IsAuthenticated, permissions.GroupMemberOrFollower,
        permissions.FulfilledProfile
    )

    def get_object(self):
        queryset = Group.objects.all()

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = generics.get_object_or_404(queryset, **filter_kwargs)

        self.private_group = obj.private

        return super(SinceMixin, self).get_object()

    def get_since_filter(self):
        serializer = serializers.SinceSerializer(
            data=self.request.query_params.dict()
        )

        post_filter = {
            'state__in': (
                Post.state_choices.READY,
                Post.state_choices.DELETED
            ),
        }

        if serializer.is_valid():
            since_filter = {
                'updated_at__gte': (
                    serializer.validated_data['since']
                    -
                    settings.YAGA_SLOP_FACTOR
                )
            }
        else:
            since_filter = {}

        post_filter.update(since_filter)

        return Q(**post_filter)


# Because of a bug in the shipped iOS client where offset is incremented
# incorrectly, always return the first 30 videos
# class FirstThirtyPlusLimitOffsetPagination(
#     LimitOffsetPagination
# ):
#     def paginate_queryset(self, queryset, request, view=None):
#         self.limit = self.get_limit(request)
#         if self.limit is None:
#             return None

#         self.offset = self.get_offset(request)
        
#         try:
#             self.count = queryset.count()
#         except (AttributeError, TypeError):
#             self.count = len(queryset)

#         self.request = request
#         if self.count > self.limit and self.template is not None:
#             self.display_page_controls = True
        
#         if (self.offset >= 50):
#             return list(chain(queryset[:50], queryset[self.offset:self.offset + self.limit]))
#         else:
#             return list(queryset[:self.offset + self.limit])
   
#     def get_next_link(self):
#         url = self.request.build_absolute_uri()
#         offset = self.offset + self.limit
        
#         return replace_query_param(url, self.offset_query_param, offset)


class PostListAPIView(
    NonAtomicView,
    SinceMixin,
    generics.ListAPIView
):
    permission_classes = (
        IsAuthenticated, permissions.FulfilledProfile
    )
    serializer_class = serializers.PostListSerializer
    pagination_class = LimitOffsetPagination

    def get_post_filter(self):
        post_filter = self.get_since_filter()

        post_filter &= self.get_visibility_filter()

        return post_filter

    def get_queryset(self):
        post_filter = self.get_post_filter()

        queryset = Post.objects.select_related(
            'user',
        ).filter(
            post_filter
        ).order_by('-ready_at')

        return queryset


class UserPostListAPIView(
    PostListAPIView
):
    def get_visibility_filter(self):
        return Q(
            # return posts for all approval states
            user=self.request.user,
        )


class GroupMemberPostListAPIView(
    PostListAPIView
):
    def get_visibility_filter(self):
        return Q(
            group__in=Group.objects.filter(
                member__user=self.request.user,
                member__status__in=[
                    Member.status_choices.MEMBER,
                    Member.status_choices.FOLLOWER
                ]
            ),
            # only return APPROVED posts
            approval=Post.approval_choices.APPROVED
        )

class GroupRetrieveUpdateAPIView(
    SafeNonAtomicView,
    PatchAsPutMixin,
    PostListAPIView,
    generics.RetrieveUpdateAPIView
):
    lookup_url_kwarg = 'group_id'
    serializer_class = serializers.GroupRetrieveSerializer
    permission_classes = (  # Anyone can retrieve info about a group.
        IsAuthenticated,
        permissions.FulfilledProfile
    )

    def get_object(self):
        queryset = Group.objects.all()

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = generics.get_object_or_404(queryset, **filter_kwargs)

        self.private_group = obj.private
        try:
            obj.member_set.get(
                user=self.request.user,
                status=Member.status_choices.MEMBER
            )
            self.is_active_member = True
        except Member.DoesNotExist:
            self.is_active_member = False

        return super(GroupRetrieveUpdateAPIView, self).get_object()

    def get_queryset(self):
        queryset = Group.objects.select_related(
            'creator'
        ).prefetch_related(
            Prefetch(
                'member_set',
                queryset=Member.objects.select_related('user').exclude(
                    status=Member.status_choices.LEFT
                )
            )
        )
        return queryset

    def perform_update(self, serializer):
        if serializer.is_valid():
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


class GroupFollowAPIView(
    PatchAsPutMixin,
    generics.UpdateAPIView,
):
    throttle_classes = (throttling.MemberScopedRateThrottle,)
    lookup_url_kwarg = 'group_id'
    permission_classes = (
        IsAuthenticated,
        permissions.PublicGroup,
        permissions.FulfilledProfile
    )

    serializer_class = serializers.GroupListSerializer

    def get_queryset(self):
        return Group.objects.all().select_related(
            'creator'
        ).prefetch_related(
            Prefetch(
                'member_set',
                queryset=Member.objects.select_related('user').exclude(
                    status=Member.status_choices.LEFT
                )
            ),
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            obj = instance.member_set.get(
                user=self.request.user
            )
        except Member.DoesNotExist:
            obj = Member()
            obj.group = instance
            obj.user = self.request.user

        if obj.status != Member.status_choices.FOLLOWER:
            obj.creator = self.request.user
            obj.status = Member.status_choices.FOLLOWER

            obj.save()

            notifications.FollowGroupNotification.schedule(
                group=obj.group.pk,
                emitter=obj.user.pk
            )

        serializer = serializers.GroupListSerializer(self.get_object())

        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )


class GroupMemberJoinUpdateAPIView(
    PatchAsPutMixin,
    generics.UpdateAPIView,
):
    throttle_classes = (throttling.MemberScopedRateThrottle,)
    lookup_url_kwarg = 'group_id'
    permission_classes = (
        IsAuthenticated, permissions.PrivateGroup,
        permissions.LeftOrContactsGroupMemeber, permissions.FulfilledProfile
    )

    serializer_class = serializers.GroupListSerializer

    def get_queryset(self):
        return Group.objects.all().select_related(
            'creator'
        ).prefetch_related(
            Prefetch(
                'member_set',
                queryset=Member.objects.select_related('user').exclude(
                    status=Member.status_choices.LEFT
                )
            ),
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            obj = instance.member_set.get(
                user=self.request.user
            )
        except Member.DoesNotExist:
            obj = Member()
            obj.group = instance
            obj.user = self.request.user

        if obj.status != Member.status_choices.PENDING:
            obj.creator = self.request.user
            obj.status = Member.status_choices.PENDING

            obj.save()

            notifications.RequestGroupNotification.schedule(
                group=obj.group.pk,
                emitter=obj.user.pk
            )

        serializer = serializers.GroupListSerializer(self.get_object())

        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )


class GroupMemberUpdateDestroyAPIView(
    GroupMemberJoinUpdateAPIView,
    generics.DestroyAPIView
):
    permission_classes = (
        IsAuthenticated, permissions.GroupMemberOrFollower,
        permissions.FulfilledProfile
    )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = serializers.GroupManageMemberAddSerializer(
            data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        self.perform_update(instance, serializer.validated_data)

        serializer = serializers.GroupListSerializer(self.get_object())

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

        if (
            serializer.validated_data['phone']
            !=
            self.request.user.phone.as_e164
        ):
            serializer = serializers.GroupListSerializer(self.get_object())

            return Response(
                dict(serializer.data),
                status=status.HTTP_200_OK
            )
        else:
            return Response(
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
                user__in=users,
                status__in=[Member.status_choices.MEMBER]
            )

            existing_users = {member.user for member in existing_members}

            new_users = users - existing_users

            new_active_users = [user for user in new_users if user.is_active]

            new_members = []

            for user in new_active_users:
                try:
                    obj = instance.member_set.get(
                        user=user
                    )

                    if obj.status == Member.status_choices.MEMBER:
                        continue
                except Member.DoesNotExist:
                    obj = Member()
                    obj.group = instance
                    obj.user = user

                obj.creator = self.request.user
                obj.status = Member.status_choices.MEMBER
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
            obj = instance.member_set.get(
                user__phone=validated_data['phone'],
                status__in=[
                    Member.status_choices.MEMBER,
                    Member.status_choices.FOLLOWER,
                    Member.status_choices.PENDING
                ]
            )
        except Member.DoesNotExist:
            pass
        else:
            previous_status = obj.status

            obj.creator = self.request.user
            obj.status = Member.status_choices.LEFT
            obj.save()

            if obj.user != self.request.user:
                if previous_status == Member.status_choices.MEMBER:
                    notifications.KickGroupNotification.schedule(
                        group=instance.pk,
                        target=obj.user.pk,
                        emitter=self.request.user.pk
                    )

                    if not obj.mute:
                        notifications.KickDirectNotification.schedule(
                            group=instance.pk,
                            target=obj.user.pk,
                            emitter=self.request.user.pk
                        )
                elif previous_status == Member.status_choices.PENDING:
                    notifications.RejectGroupNotification.schedule(
                        group=instance.pk,
                        target=obj.user.pk,
                        emitter=self.request.user.pk
                    )

                    # if not obj.mute:
                    #     notifications.RejectDirectNotification.schedule(
                    #         group=instance.pk,
                    #         target=obj.user.pk,
                    #         emitter=self.request.user.pk
                    #     )


class GroupMemberMuteAPIView(
    NonAtomicView,
    PatchAsPutMixin,
    generics.UpdateAPIView,
):
    lookup_url_kwarg = 'group_id'
    permission_classes = (
        IsAuthenticated, permissions.GroupMemeber,
        permissions.FulfilledProfile
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

        serializer = serializers.MemberSerializer(serializer.instance)

        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )


class PostListCreateAPIView(
    NonAtomicView,
    SinceMixin,
    generics.ListCreateAPIView
):
    lookup_url_kwarg = 'group_id'
    serializer_class = serializers.PostSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (
        IsAuthenticated,
        permissions.GroupMemberOrFollower, # NOT ONLY GROUP MEMBER BECAUSE FOLLOWERS CAN POST
        permissions.FulfilledProfile
    )

    def get_throttles(self):
        if self.request.method != 'GET':
            return [throttling.PostScopedRateThrottle()]
        else:
            return []

    def get_post_filter(self):
        post_filter = (self.get_since_filter() & Q(
            group=self.kwargs['group_id']
        ))

        return post_filter

    def get_queryset(self):
        post_filter = self.get_post_filter()
        queryset = Post.objects.select_related(
            'user',
        ).filter(
            post_filter
        ).order_by('-ready_at')
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        obj = Post()
        obj.user = request.user
        obj.group = generics.get_object_or_404(
            Group.objects.all(),
            pk=self.kwargs['group_id']
        )

        if obj.group.private or obj.group.active_member_set().filter(
            user=obj.user
        ).exists():
            obj.approval = Post.approval_choices.APPROVED

        if serializer.validated_data.get('name'):
            obj.namer = request.user

            for key, value in list(serializer.validated_data.items()):
                setattr(obj, key, value)

        obj.upload_version = self.request.bridge.yaga.CLIENT_VERSION
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
        )

    def perform_update(self, serializer):
        if serializer.validated_data.get('name'):
            serializer.validated_data['namer'] = self.request.user

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


class PostApproveAPIView(
    PostAPIView,
    generics.UpdateAPIView
):
    serializer_class = serializers.PostSerializer
    permission_classes = (
        IsAuthenticated, permissions.PostGroupMember,
        permissions.FulfilledProfile
    )

    def get_queryset(self):
        return Post.objects.all()

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.mark_approved()

        serializer = self.get_serializer(obj)
        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )


class PostRejectAPIView(
    PostAPIView,
    generics.UpdateAPIView
):
    serializer_class = serializers.PostSerializer
    permission_classes = (
        IsAuthenticated, permissions.PostGroupMember,
        permissions.FulfilledProfile
    )

    def get_queryset(self):
        return Post.objects.all()

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.mark_rejected()

        serializer = self.get_serializer(obj)
        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )


class PostCopyUpdateAPIView(
    PostAPIView,
    PatchAsPutMixin,
    generics.UpdateAPIView
):
    throttle_classes = (throttling.PostScopedRateThrottle,)
    serializer_class = serializers.PostCopyGroupSerializer
    permission_classes = (
        IsAuthenticated, permissions.PostOwner,
        permissions.AvailablePost, permissions.FulfilledProfile
    )

    def get_queryset(self):
        return Post.objects.all()

    def post(self, request, *args, **kwargs):
        return super(
            PostCopyUpdateAPIView, self
        ).put(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        if request.method == 'PUT':
            raise MethodNotAllowed(request.method)

        return super(
            PostCopyUpdateAPIView, self
        ).get(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        posts = self.perform_copy(serializer)

        if posts:
            action_status = status.HTTP_201_CREATED
        else:
            action_status = status.HTTP_200_OK

        # if posts:
        #     serializer.instance.schedule_copy_notifications(posts)

        serializer = serializers.PostCopySerializer(
            posts,
            many=True
        )

        return Response(
            list(serializer.data),
            status=action_status
        )

    def perform_copy(self, serializer):
        posts = []

        if serializer.validated_data.get('groups'):
            copied_groups = PostCopy.objects.filter(
                parent=serializer.instance
            ).values_list('group', flat=True)

            groups = Group.objects.filter(
                Q(
                    pk__in=serializer.validated_data['groups'],
                    member__user=self.request.user,
                    member__status=Member.status_choices.MEMBER,
                    private=True
                )
                |
                Q(
                    pk__in=serializer.validated_data['groups'],
                    private=False
                )
            ).exclude(
                pk__in=copied_groups
            ).exclude(
                pk=serializer.instance.group.pk
            )

            for group in groups:
                copy = PostCopy()
                copy.parent = serializer.instance
                copy.group = group

                post = Post()
                post.state = Post.state_choices.PENDING
                post.user = self.request.user
                post.group = group

                if group.private or group.active_member_set().filter(
                    user=post.user
                ).exists():
                    post.approval = Post.approval_choices.APPROVED

                for attr in PostCopy.copy_attrs:
                    setattr(
                        post,
                        attr,
                        getattr(
                            copy.parent, attr
                        )
                    )

                post.save()

                copy.post = post

                if copy.parent.checksum:
                    if post.group.post_set.filter(
                        checksum=copy.parent.checksum
                    ).exists():
                        continue

                try:
                    with transaction.atomic():
                        copy.save()

                    posts.append(post)

                except IntegrityError:
                    with transaction.atomic():
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
        return Post.objects.select_related(
            'user',
            'namer'
        )

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

            if obj.user != obj.post.user and obj.post.group.private:
                notifications.LikeDirectNotification.schedule(
                    post=obj.post.pk,
                    emitter=obj.user.pk
                )

        serializer = self.get_serializer(instance)

        return Response(
            dict(serializer.data),
            status=status.HTTP_200_OK
        )


class PostRetrieveAPIView(
    NonAtomicView,
    generics.RetrieveAPIView
):
    lookup_url_kwarg = 'post_id'
    serializer_class = serializers.PublicPostSerializer
    renderer_classes = jsonp_renderer

    def get_queryset(self):
        return Post.objects.select_related(
            'user'
        ).filter(
            approval=Post.approval_choices.APPROVED,
            state=Post.state_choices.READY
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
        super(
            ContactListCreateAPIView, self
        ).post(request, *args, **kwargs)

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
