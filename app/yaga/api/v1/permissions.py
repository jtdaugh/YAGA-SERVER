from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import Token

from ...models import Contact, Member, Post


class TokenOwner(
    BasePermission
):
    def has_object_permission(self, request, view, obj):
        return isinstance(obj, Token) and request.user == obj.user


class GroupMemeber(
    BasePermission
):
    def has_object_permission(self, request, view, obj):
        return obj.member_set.filter(
            user=request.user,
            status=Member.status_choices.MEMBER
        ).exists()


class NotGroupMemeber(
    GroupMemeber
):
    def has_object_permission(self, request, view, obj):
        return not super(NotGroupMemeber, self).has_object_permission(
            request, view, obj
        )

class GroupFollower(
    BasePermission
):
    def has_object_permission(self, request, view, obj):
        return obj.member_set.filter(
            user=request.user,
            status=Member.status_choices.FOLLOWER
        ).exists()


class GroupMemberOrFollower(
    BasePermission
):
    def has_object_permission(self, request, view, obj):
        return obj.member_set.filter(
            user=request.user,
            status__in=[
                Member.status_choices.MEMBER, 
                Member.status_choices.FOLLOWER,
            ]
        ).exists()


class LeftOrContactsGroupMemeber(
    BasePermission
):
    def has_object_permission(self, request, view, obj):
        if obj.member_set.filter(
            user=request.user,
            status__in=[
                Member.status_choices.LEFT,
                Member.status_choices.PENDING,
            ]
        ).exists():
            return True

        contact = Contact.objects.filter(user=request.user).first()

        phones = []

        if contact and contact.phones:
            for phone in contact.phones:
                phones.append(phone)

        for contact in Contact.objects.select_related(
            'user'
        ).filter(
            phones__contains=[request.user.phone.as_e164],
        ):
            phones.append(contact.user.phone.as_e164)

        phones = list(set(phones))

        if not phones:
            return False
        else:
            return obj.member_set.filter(
                user__phone__in=phones,
                status=Member.status_choices.MEMBER
            ).exists()


class PostGroupMember(
    GroupMemeber
):
    def has_object_permission(self, request, view, obj):
        return super(PostGroupMember, self).has_object_permission(
            request, view, obj.group
        )


class PostOwnerOrPostGroupMember(
    PostGroupMember
):
    def has_object_permission(self, request, view, obj):
        if request.method not in SAFE_METHODS + ('PATCH', 'PUT'):
            return obj.user == request.user
        else:
            return super(
                PostOwnerOrPostGroupMember, self
            ).has_object_permission(
                request, view, obj
            )


class PostOwner(
    BasePermission
):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class PrivateGroup(
    BasePermission
):
    def has_object_permission(self, request, view, obj):
        return obj.private


class PublicGroup(
    PrivateGroup
):
    def has_object_permission(self, request, view, obj):
        return not super(PublicGroup, self).has_object_permission(
            request, view, obj
        )


class AvailablePost(
    BasePermission
):
    def has_object_permission(self, request, view, obj):
        if obj.state == Post.state_choices.DELETED:
            return False

        if obj.state == Post.state_choices.READY:
            return True

        return obj.user == request.user


class IsAnonymous(
    BasePermission
):
    def has_permission(self, request, view):
        return request.user and request.user.is_anonymous()


class FulfilledProfile(
    BasePermission
):
    def has_permission(self, request, view):
        return request.user.name is not None


class EmptyProfile(
    BasePermission
):
    def has_object_permission(self, request, view, obj):
        return obj.name is None
