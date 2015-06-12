# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime
from django.conf import settings


def populate_owner(apps, schema_editor):
    Post = apps.get_model('yaga', 'Post')

    for post in Post.objects.all():
        post.owner = post.user
        post.save()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yaga', '0021_postcopy'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='owner',
            field=models.ForeignKey(related_name='owner', default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True, verbose_name='User'),
        ),
        migrations.AddField(
            model_name='postcopy',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 10, 15, 18, 51, 373070, tzinfo=utc), verbose_name='Created At', auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='post',
            name='user',
            field=models.ForeignKey(related_name='user', verbose_name='User', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(populate_owner),
    ]
