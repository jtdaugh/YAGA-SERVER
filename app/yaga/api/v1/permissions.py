from __future__ import absolute_import, division, unicode_literals


from rest_framework.permissions import BasePermission


class TokenAuth(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.auth
            and
            request.auth == obj
        )


class GroupMemeber(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.member_set.filter(
            user=request.user
        ).exists()


class PostGroupMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.group.member_set.filter(
            user=request.user
        ).exists()


class PostOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAnonymous(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_anonymous()
