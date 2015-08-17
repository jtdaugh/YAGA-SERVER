# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0038_auto_20150817_0947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='follow',
            field=models.BooleanField(default=False, db_index=True, verbose_name='Follow'),
        ),
    ]
