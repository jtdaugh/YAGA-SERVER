# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0044_clean_up_pair_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='status',
            field=models.PositiveSmallIntegerField(default=0, db_index=True, verbose_name='Status', choices=[(0, 'MEMBER'), (1, 'FOLLOWER'), (10, 'PENDING'), (5, 'LEFT')]),
        ),
    ]
