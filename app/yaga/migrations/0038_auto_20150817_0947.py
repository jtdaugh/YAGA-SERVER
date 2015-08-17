# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from ..choices import ApprovalChoice


def approval_migration(apps, schema_editor):
    Post = apps.get_model('yaga', 'Post')

    approval_choices = ApprovalChoice()

    for post in Post.objects.all():
        if post.approved:
            post.approval = approval_choices.APPROVED
        else:
            post.approval = approval_choices.WAITING


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0037_auto_20150714_1756'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='approval',
            field=models.PositiveSmallIntegerField(default=0, db_index=True, verbose_name='Approval State', choices=[(0, 'WAITING'), (1, 'APPROVED'), (5, 'REJECTED')]),
        ),
        migrations.RunPython(approval_migration),
        migrations.RemoveField(
            model_name='post',
            name='approved',
        ),
        migrations.AddField(
            model_name='group',
            name='featured',
            field=models.BooleanField(default=False, verbose_name='Featured'),
        ),
        migrations.AddField(
            model_name='member',
            name='follow',
            field=models.BooleanField(default=False, verbose_name='Follow'),
        ),
        migrations.AlterField(
            model_name='member',
            name='status',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Status', choices=[(0, 'MEMBER'), (1, 'FOLLOWER'), (10, 'PENDING'), (5, 'LEFT')]),
        ),
    ]
