# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import app.model_fields
import yaga.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Code',
            fields=[
                ('request_id', models.CharField(max_length=255, serialize=False, verbose_name='Request Id', primary_key=True)),
                ('phone', app.model_fields.PhoneNumberField(unique=True, max_length=255, verbose_name='Phone Number')),
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
                ('id', app.model_fields.UUIDField(max_length=32, serialize=False, editable=False, primary_key=True, blank=True)),
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
            name='Like',
            fields=[
                ('id', app.model_fields.UUIDField(max_length=32, serialize=False, editable=False, primary_key=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
            ],
            options={
                'verbose_name': 'Like',
                'verbose_name_plural': 'Likes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', app.model_fields.UUIDField(max_length=32, serialize=False, editable=False, primary_key=True, blank=True)),
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
                ('id', app.model_fields.UUIDField(primary_key=True, serialize=False, editable=False, max_length=32, version=1, blank=True)),
                ('name', models.CharField(max_length=255, null=True, verbose_name='Name', blank=True)),
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
            model_name='like',
            name='post',
            field=models.ForeignKey(verbose_name='Post', to='yaga.Post'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='like',
            name='user',
            field=models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='like',
            unique_together=set([('user', 'post')]),
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Members', through='yaga.Member', db_index=True),
            preserve_default=True,
        ),
    ]
