# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def update_checksum(apps, schema_editor):
    Post = apps.get_model('yaga', 'Post')

    for post in Post.objects.filter(
        deleted=True
    ):
        post.checksum = None
        post.save()


def remove_dups(apps, schema_editor):
    Group = apps.get_model('yaga', 'Group')

    for group in Group.objects.all():
        for post in group.post_set.filter(
            ready=True,
            deleted=False
        ).distinct('checksum'):
            if post.checksum is not None:
                for dup in group.post_set.filter(
                    checksum=post.checksum
                ).exclude(
                    pk=post.pk
                ):
                    dup.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0007_auto_20150409_1533'),
    ]

    operations = [
        migrations.RunPython(update_checksum),
        migrations.RunPython(remove_dups),
    ]
