# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0027_auto_20150612_1201'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='status',
            field=models.PositiveSmallIntegerField(default=0, db_index=True, verbose_name='Status', choices=[(0, 'MEMBER'), (10, 'PENDING'), (5, 'LEFT')]),
        ),
    ]
