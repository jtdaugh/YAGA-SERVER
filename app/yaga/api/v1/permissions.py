from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from rest_framework.permissions import BasePermission

from accounts.models import Token


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
            user=request.user
        ).exists()


class PostGroupMember(
    BasePermission
):
    def has_object_permission(self, request, view, obj):
        return obj.group.member_set.filter(
            user=request.user
        ).exists()


class PostOwner(
    BasePermission
):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class AvailablePost(
    BasePermission
):
    def has_object_permission(self, request, view, obj):
        return (obj.ready and not obj.deleted)


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
    def has_permission(self, request, view):
        return request.user.name is None
