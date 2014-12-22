from __future__ import absolute_import, division, unicode_literals

import string

from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.conf import settings
from django.db import models, IntegrityError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.crypto import get_random_string
from django.core.exceptions import ObjectDoesNotExist
from phonenumber_field.modelfields import PhoneNumberField

from app.utils import reverse_host


class UserManager(
    BaseUserManager
):
    def __create_user(
        self, phone, password, **extra_fields
    ):
        now = timezone.now()

        if not phone:
            raise ValueError('The given phone must be set')

        name = extra_fields.pop('name', None)
        is_active = extra_fields.pop('is_active', True)
        is_staff = extra_fields.pop('is_staff', False)
        is_superuser = extra_fields.pop('is_superuser', False)

        user = self.model(
            phone=phone,
            name=name,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_user(self, phone, password, **extra_fields):
        return self.__create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.update({
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        })
        return self.__create_user(phone, password, **extra_fields)

    def get_or_create(self, **kwargs):
        phone = kwargs.pop('phone')

        try:
            user = self.get(
                phone=phone
            )
        except ObjectDoesNotExist:
            user = self.create_user(
                phone, None
            )

        return user


class AbstractUser(
    AbstractBaseUser,
    PermissionsMixin
):
    phone = PhoneNumberField(
        verbose_name=_('Phone Number'),
        max_length=255,
        unique=True,
        db_index=True
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        unique=True,
        db_index=True,
        null=True,
        blank=True
    )

    is_staff = models.BooleanField(
        verbose_name=_('Staff status'), default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'
        )
    )

    is_active = models.BooleanField(
        verbose_name=_('Active'), default=True,
        help_text=_(
            'Designates whether this user should be treated as '
            'active. Unselect this instead of deleting accounts.'
        )
    )

    date_joined = models.DateTimeField(
        verbose_name=_('Date joined'), default=timezone.now
    )

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    class Meta:
        abstract = True
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def get_username(self):
        if self.name:
            return self.name

        return self.phone.as_e164

    def get_full_name(self):
        return self.get_username()

    def get_short_name(self):
        return self.get_username()

    def username(self):
        return self.get_username()

    def __unicode__(self):
        return self.get_username()

    def __str__(self):
        return self.get_username()

    def get_admin_url(self):
        return reverse(
            'admin:accounts_user_change', args=(self.pk,)
        )

    def get_admin_absolute_url(self):
        return reverse_host(self.get_admin_url())


class User(
    AbstractUser
):
    class Meta(
        AbstractUser.Meta
    ):
        swappable = 'AUTH_USER_MODEL'


class Token(models.Model):
    KEY_LENGTH = 128
    KEY_CHARS = string.ascii_letters + string.digits

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('User'),
        db_index=True,
    )

    key = models.CharField(
        verbose_name=_('Key'),
        max_length=255,
        blank=True,
        unique=True,
        db_index=True
    )

    created_at = models.DateTimeField(
        verbose_name=_('Created At'),
        auto_now_add=True
    )

    def save(self, *args, **kwargs):
        if not self.key:
            while True:
                try:
                    self.key = self.generate_key()

                    return super(Token, self).save(*args, **kwargs)
                except IntegrityError:
                    continue
        else:
            return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return get_random_string(self.KEY_LENGTH, self.KEY_CHARS)

    def __str__(self):
        return self.key
