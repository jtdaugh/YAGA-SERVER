from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from decimal import Decimal

import regex
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from accounts.models import Token

from ...conf import settings
from ...models import Code, Contact, Device, Group, Member, Post
from .fields import CodeField, PhoneField, TimeStampField, UnicodeField
from .validators import UniqueLowerUserName


class NonStrictListField(
    serializers.ListField
):
    def to_internal_value(self, data):
        if isinstance(data, type('')) or not hasattr(data, '__iter__'):
            self.fail('not_a_list', input_type=type(data).__name__)

        res = []

        for item in data:
            try:
                res.append(self.child.run_validation(item))
            except ValidationError:
                pass

        return res


class UniqueNonStrictListField(
    serializers.ListField
):
    def to_internal_value(self, data):
        if isinstance(data, type('')) or not hasattr(data, '__iter__'):
            self.fail('not_a_list', input_type=type(data).__name__)

        res = []

        for item in data:
            try:
                item = self.child.run_validation(item)

                if item not in res:
                    res.append(item)
            except ValidationError:
                pass

        return res


class SinceSerializer(
    serializers.Serializer
):
    since = TimeStampField()


class UserSerializer(
    serializers.ModelSerializer
):
    name = UnicodeField(
        required=False, numeric=False, validators=[UniqueLowerUserName()]
    )

    class Meta:
        model = get_user_model()
        read_only_fields = ('phone',)
        fields = ('phone', 'name', 'id')


class AuthStatusResponseSerializer(
    serializers.Serializer
):
    expire_at = serializers.DateTimeField()


class TokenResponseSerializer(
    serializers.Serializer
):
    token = serializers.CharField()


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


class LikerSerializer(
    UserSerializer
):
    def to_representation(self, obj):
        return super(LikerSerializer, self).to_representation(obj.user)


class PostSerializer(
    serializers.ModelSerializer
):
    name = UnicodeField(required=False, spaces=True, max_length=200)

    user = UserSerializer(read_only=True)

    namer = UserSerializer(read_only=True)

    likers = LikerSerializer(read_only=True, many=True, source='like_set')

    font = serializers.IntegerField(
        required=False, min_value=0, max_value=20
    )

    name_x = serializers.DecimalField(
        required=False,
        min_value=Decimal(-255.0000), max_value=Decimal(255.0000),
        max_digits=7, decimal_places=4,
    )

    name_y = serializers.DecimalField(
        required=False,
        min_value=Decimal(-255.0000), max_value=Decimal(255.0000),
        max_digits=7, decimal_places=4,
    )

    rotation = serializers.DecimalField(
        required=False,
        min_value=Decimal(-255.0000), max_value=Decimal(255.0000),
        max_digits=7, decimal_places=4,
    )

    scale = serializers.DecimalField(
        required=False,
        min_value=Decimal(-255.0000), max_value=Decimal(255.0000),
        max_digits=7, decimal_places=4
    )

    miscellaneous = UnicodeField(required=False, spaces=True, max_length=255)

    ready = serializers.BooleanField(
        read_only=True
    )

    deleted = serializers.BooleanField(
        read_only=True
    )

    class Meta:
        model = Post
        caption_fields = (
            'font', 'name_x', 'name_y', 'rotation', 'scale', 'miscellaneous'
        )
        fields = (
            'attachment', 'attachment_preview', 'ready_at', 'updated_at',
            'user', 'id', 'name', 'ready', 'deleted', 'likers', 'namer'
        ) + caption_fields
        read_only_fields = (
            'attachment', 'attachment_preview', 'ready_at', 'deleted'
        )

    def validate(self, attrs):
        if ((
            self.instance is None
            and
            attrs.get('name') is None
        ) or (
            self.instance is not None
            and
            self.instance.name is None
            and
            attrs.get('name') is None
        )):
            if (
                len(set(self.Meta.caption_fields) & set(list(attrs.keys())))
                !=
                0
            ):
                msg = _('Can not set caption attributes without name.')
                raise ValidationError(msg)
        else:
            coords = ('name_y', 'name_x')

            def _bool(value):
                value = attrs.get(value)

                if value == 0:
                    return True

                return bool(value)

            if _bool(coords[0]) ^ _bool(coords[1]):
                msg = _('Options name_x and name_y must be set together.')
                raise ValidationError(msg)

        return attrs

    def update(self, instance, validated_data):
        with transaction.atomic():
            post = instance.atomic

            if post:
                return super(
                    PostSerializer, self
                ).update(post, validated_data)
            else:
                return instance


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
    name = UnicodeField(required=True, spaces=True)

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
    phones = NonStrictListField(
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
    vendor = serializers.CharField()

    class Meta:
        model = Device
        fields = ('vendor', 'token', 'locale')

    def to_representation(self, instance):
        ret = super(DeviceSerializer, self).to_representation(instance)

        ret['vendor'] = Device.vendor_choices.value(
            int(ret['vendor'])
        )

        return ret

    def get_validators(self):
        validators = super(DeviceSerializer, self).get_validators()

        for validator in validators:
            if isinstance(validator, UniqueTogetherValidator):
                validators.remove(validator)

        return validators

    def save(self, **kwargs):
        instance = Device.objects.filter(
            token=self.validated_data['token'],
            vendor=self.validated_data['vendor']
        ).first()

        if instance:
            self.instance = instance

            if (
                self.instance.user == kwargs['user']
                and
                self.instance.locale == self.validated_data['locale']
            ):
                self.instance.save(update_fields=['updated_at'])

                return self.instance

        return super(DeviceSerializer, self).save(**kwargs)

    def validate_vendor(self, value):
        try:
            vendor = Device.vendor_choices.key(value)

            return vendor
        except KeyError:
            pass

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

        if vendor == Device.vendor_choices.IOS:
            if len(token) != 64:
                msg = _('Invalid token.')
                raise ValidationError(msg)

        if locale.lower() not in [
            code.lower() for code, title in settings.LANGUAGES
        ]:
            locale = settings.LANGUAGE_CODE.lower()

        attrs['locale'] = locale

        return attrs


class UserSearchSerializer(
    serializers.Serializer
):
    phones = NonStrictListField(
        child=PhoneField()
    )


class ContactSerializer(
    serializers.ModelSerializer
):
    phones = UniqueNonStrictListField(
        child=PhoneField(),
    )

    class Meta:
        fields = ('phones',)
        model = Contact
