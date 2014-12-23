from __future__ import absolute_import, division, unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError

from accounts.models import Token
from .fields import PhoneField, CodeField
from ...models import Code, Group


class UserRetrieveSerializer(
    ModelSerializer
):
    class Meta:
        model = get_user_model()
        fields = ('phone', 'name')


class UserUpdateSerializer(
    UserRetrieveSerializer
):
    class Meta(
        UserRetrieveSerializer.Meta
    ):
        fields = ('name',)


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


class GroupSerializer(
    ModelSerializer
):
    members = UserRetrieveSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ('name', 'members', 'id')


class GroupManageSerializer(
    GroupSerializer
):
    phone = PhoneField()

    class Meta(
        GroupSerializer.Meta
    ):
        fields = ('phone',)
