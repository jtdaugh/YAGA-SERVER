from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.db.models import Q
from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import Token

from ...models import Contact, Group, Member, Post


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


class ContactsGroupMemeber(
    BasePermission
):
    def has_object_permission(self, request, view, obj):
        contact = Contact.objects.filter(user=request.user).first()

        if contact:
            phone_query = Q()

            for phone in contact.phones:
                phone_query |= Q(
                    member__user__phone=phone,
                    member__status=Member.status_choices.MEMBER
                )

            return Group.objects.filter(
                Q(member__user__name__isnull=False)
                &
                phone_query
            ).filter(
                pk=obj.pk
            ).exists()

        return False


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
