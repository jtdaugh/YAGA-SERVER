from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import regex
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from accounts.models import Token

from ...conf import settings
from ...models import Code, Device, Group, Member, Post
from .fields import CodeField, PhoneField, TimeStampField


class SinceSerializer(
    serializers.Serializer
):
    since = TimeStampField()


class UserSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = get_user_model()
        read_only_fields = ('phone',)
        fields = ('phone', 'name', 'id')


class TokenSerializer(
    serializers.ModelSerializer
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
    serializers.ModelSerializer
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
    serializers.ModelSerializer
):
    user = UserSerializer(read_only=True)
    likers = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Post
        fields = (
            'attachment', 'ready_at', 'updated_at',
            'user', 'id', 'name', 'deleted', 'likers'
        )
        read_only_fields = ('attachment', 'ready_at', 'deleted')


class MemberSerializer(
    serializers.ModelSerializer
):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = ('user', 'joined_at', 'mute')


class GroupSerializer(
    serializers.ModelSerializer
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
        fields = ('name', 'members', 'id', 'updated_at')


class GroupRetrieveSerializer(
    GroupSerializer
):
    posts = PostSerializer(
        many=True, read_only=True, source='post_set'
    )

    class Meta(
        GroupSerializer.Meta
    ):
        fields = ('name', 'members', 'posts', 'id', 'updated_at')


class GroupManageMemberAddSerializer(
    GroupSerializer
):
    phones = serializers.ListField(
        child=PhoneField()
    )

    names = serializers.ListField(
        child=serializers.CharField()
    )

    class Meta(
        GroupSerializer.Meta
    ):
        fields = ('phones', 'names')


class GroupManageMemberRemoveSerializer(
    GroupSerializer
):
    phone = PhoneField()

    class Meta(
        GroupSerializer.Meta
    ):
        fields = ('phone', )


class DeviceSerializer(
    serializers.ModelSerializer
):
    user = UserSerializer(read_only=True)
    vendor = serializers.CharField()

    class Meta:
        model = Device

    def to_representation(self, instance):
        ret = super(DeviceSerializer, self).to_representation(instance)

        model_vendor = int(ret['vendor'])

        for vendor, value in self.Meta.model.VENDOR_CHOICES:
            if vendor == model_vendor:
                ret['vendor'] = value
                break

        return ret

    def get_validators(self):
        validators = super(DeviceSerializer, self).get_validators()

        for validator in validators:
            if isinstance(validator, UniqueTogetherValidator):
                validators.remove(validator)

        return validators

    def save(self, **kwargs):
        instance = self.Meta.model.objects.filter(
            token=self.validated_data['token'],
            vendor=self.validated_data['vendor']
        ).first()

        if instance is not None:
            self.instance = instance

            if (
                self.instance.user == kwargs['user']
                and
                self.instance.locale == self.validated_data['locale']
            ):
                return self.instance

        return super(DeviceSerializer, self).save(**kwargs)

    def validate_vendor(self, value):
        if value == self.Meta.model.IOS_VALUE:
            return self.Meta.model.IOS

        msg = _('Unsupported vendor.')
        raise ValidationError(msg)

    def validate_token(self, value):
        if not regex.match(r'[a-z0-9]+', value):
            msg = _('Invalid token.')
            raise ValidationError(msg)

        return value

    def validate(self, attrs):
        vendor = attrs['vendor']
        token = attrs['token']
        locale = attrs['locale']

        if vendor == Device.IOS:
            if len(token) != 64:
                msg = _('Invalid token.')
                raise ValidationError(msg)

        if locale not in [code for code, title in settings.LANGUAGES]:
            locale = settings.LANGUAGE_CODE

        attrs['locale'] = locale

        return attrs


class UserSearchSerializer(
    serializers.Serializer
):
    phones = serializers.ListField(
        child=PhoneField()
    )
