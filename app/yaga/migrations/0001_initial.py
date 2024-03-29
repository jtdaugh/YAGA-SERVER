# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djorm_pgarray.fields
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
            name='Contact',
            fields=[
                ('id', app.model_fields.UUIDField(max_length=32, serialize=False, editable=False, primary_key=True, blank=True)),
                ('phones', djorm_pgarray.fields.TextArrayField(dbtype='text', verbose_name='phone')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('user', models.OneToOneField(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Contact',
                'verbose_name_plural': 'Contacts',
            },
            bases=(models.Model,),
        ),
        migrations.RunSQL('''
            CREATE INDEX yaga_contact_gin
            on yaga_contact
            USING gin
            (phones)
        '''),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', app.model_fields.UUIDField(max_length=32, serialize=False, editable=False, primary_key=True, blank=True)),
                ('vendor', models.PositiveSmallIntegerField(db_index=True, verbose_name='Vendor', choices=[(0, 'IOS'), (1, 'ANDROID')])),
                ('locale', models.CharField(max_length=2, verbose_name='Locale')),
                ('token', models.CharField(max_length=255, verbose_name='Token', db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Device',
                'verbose_name_plural': 'Devices',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', app.model_fields.UUIDField(max_length=32, serialize=False, editable=False, primary_key=True, blank=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At', db_index=True)),
                ('creator', models.ForeignKey(related_name='group_creator', verbose_name='Creator', to=settings.AUTH_USER_MODEL)),
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
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At', db_index=True)),
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
                ('creator', models.ForeignKey(related_name='member_creator', verbose_name='Creator', to=settings.AUTH_USER_MODEL)),
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
                ('name_x', models.PositiveSmallIntegerField(null=True, verbose_name='Name X', blank=True)),
                ('name_y', models.PositiveSmallIntegerField(null=True, verbose_name='Name Y', blank=True)),
                ('font', models.PositiveSmallIntegerField(null=True, verbose_name='Font', blank=True)),
                ('attachment', models.FileField(upload_to=yaga.models.post_upload_to, null=True, verbose_name='Attachment', blank=True)),
                ('checksum', models.CharField(max_length=255, null=True, verbose_name='Checksum', blank=True)),
                ('mime', models.CharField(max_length=255, null=True, verbose_name='Mime', blank=True)),
                ('ready', models.BooleanField(default=False, db_index=True, verbose_name='Ready')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('ready_at', models.DateTimeField(db_index=True, null=True, verbose_name='Ready At', blank=True)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At', db_index=True)),
                ('deleted', models.BooleanField(default=False, db_index=True, verbose_name='Deleted')),
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
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Members', through='yaga.Member'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='device',
            unique_together=set([('vendor', 'token')]),
        ),
    ]
