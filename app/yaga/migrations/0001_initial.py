# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import yaga.models
from django.conf import settings
import uuidfield.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Code',
            fields=[
                ('request_id', models.CharField(max_length=255, serialize=False, verbose_name='Request Id', primary_key=True)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(unique=True, max_length=255, verbose_name='Phone Number')),
                ('expire_at', models.DateTimeField(default=yaga.models.code_expire_at, verbose_name='Expire At', db_index=True)),
            ],
            options={
                'verbose_name': 'Code',
                'verbose_name_plural': 'Codes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', uuidfield.fields.UUIDField(primary_key=True, serialize=False, editable=False, max_length=32, blank=True, unique=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
            ],
            options={
                'verbose_name': 'Group',
                'verbose_name_plural': 'Groups',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', uuidfield.fields.UUIDField(primary_key=True, serialize=False, editable=False, max_length=32, blank=True, unique=True)),
                ('mute', models.BooleanField(default=False, db_index=True, verbose_name='Mute')),
                ('joined_at', models.DateTimeField(auto_now_add=True, verbose_name='Joined At')),
                ('group', models.ForeignKey(verbose_name='Group', to='yaga.Group')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Member',
                'verbose_name_plural': 'Members',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', uuidfield.fields.UUIDField(primary_key=True, serialize=False, editable=False, max_length=32, blank=True, unique=True)),
                ('attachment', models.FileField(db_index=True, upload_to=yaga.models.post_upload_to, null=True, verbose_name='Attachment', blank=True)),
                ('checksum', models.CharField(db_index=True, max_length=255, null=True, verbose_name='Checksum', blank=True)),
                ('mime', models.CharField(db_index=True, max_length=255, null=True, verbose_name='MIme', blank=True)),
                ('ready', models.BooleanField(default=False, db_index=True, verbose_name='Ready')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('ready_at', models.DateTimeField(db_index=True, null=True, verbose_name='Ready At', blank=True)),
                ('group', models.ForeignKey(verbose_name='Group', to='yaga.Group')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Post',
                'verbose_name_plural': 'Posts',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='member',
            unique_together=set([('user', 'group')]),
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Members', through='yaga.Member', db_index=True),
            preserve_default=True,
        ),
    ]
