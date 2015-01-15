# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0003_auto_20150115_0234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='token',
            field=models.CharField(max_length=255, verbose_name='Token', db_index=True),
            preserve_default=True,
        ),
    ]
