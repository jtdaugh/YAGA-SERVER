# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from ..choices import ApprovalChoice

class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0038_post_approval'),
    ]

    operations = [
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
