from __future__ import absolute_import, division, unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework.serializers import (
    ModelSerializer, ListField, Serializer
)
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError

from accounts.models import Token
from .fields import PhoneField, CodeField, TimeStampField
from ...models import Code, Group, Post, Member


class SinceSerializer(
    Serializer
):
    since = TimeStampField()


class UserSerializer(
    ModelSerializer
):
    class Meta:
        model = get_user_model()
        read_only_fields = ('phone',)
        fields = ('phone', 'name', 'id')


class TokenSerializer(
    ModelSerializer
):
    phone = PhoneField()
    code = CodeField(min_length=4, max_length=4)

    class Meta:
        model = Token
        fields = ('phone', 'code')

    def validate(self, attrs):
        phone = attrs['phone']
        code = attrs['code']

        if phone and code:
            user = authenticate(phone=phone, code=code)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise ValidationError(msg)
            else:
                msg = _('Unable to log in with provided credentials.')
                raise ValidationError(msg)
        else:
            msg = _('Must include "phone" and "code"')
            raise ValidationError(msg)

        attrs['user'] = user

        return attrs

    def create(self, validated_data):
        user = validated_data['user']

        token = Token()
        token.user = user
        token.save()

        return token


class CodeRetrieveSerializer(
    ModelSerializer
):
    phone = PhoneField()

    class Meta:
        model = Code
        fields = ('phone',)


class CodeCreateSerializer(
    CodeRetrieveSerializer
):
    phone = PhoneField(
        validators=[
            UniqueValidator(
                queryset=Code.objects.all(),
                message=_('Concurrent code request.')
            )
        ]
    )

    def validate(self, attrs):
        phone = attrs['phone']

        model = get_user_model()

        if model.objects.filter(
            phone=phone,
            is_active=False
        ).exists():
            msg = _('User account is disabled.')
            raise ValidationError(msg)

        return attrs


class PostSerializer(
    ModelSerializer
):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ('attachment', 'ready_at', 'user', 'id')


class MemberSerializer(
    ModelSerializer
):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = ('user', 'joined_at', 'mute')


class GroupSerializer(
    ModelSerializer
):
    members = MemberSerializer(many=True, read_only=True, source='member_set')

    class Meta:
        model = Group


class GroupListSerializer(
    GroupSerializer
):
    class Meta(
        GroupSerializer.Meta
    ):
        fields = ('name', 'members', 'id')


class GroupRetrieveSerializer(
    GroupSerializer
):
    posts = PostSerializer(many=True, read_only=True, source='post_set')

    class Meta(
        GroupSerializer.Meta
    ):
        fields = ('name', 'members', 'posts', 'id')


class GroupManageMemberAddSerializer(
    GroupSerializer
):
    phones = ListField(
        child=PhoneField()
    )

    class Meta(
        GroupSerializer.Meta
    ):
        fields = ('phones', )


class GroupManageMemberRemoveSerializer(
    GroupSerializer
):
    phone = PhoneField()

    class Meta(
        GroupSerializer.Meta
    ):
        fields = ('phone', )
