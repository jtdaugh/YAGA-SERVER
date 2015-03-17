# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


def update_namers(apps, schema_editor):
    Post = apps.get_model('yaga', 'Post')

    for post in Post.objects.filter(
        ready=True
    ).exclude(
        name__isnull=True
    ):
        post.namer = post.user
        post.save()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yaga', '0002_monkeyuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='namer',
            field=models.ForeignKey(related_name='post_namer', verbose_name='Namer', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.RunPython(update_namers)
    ]
