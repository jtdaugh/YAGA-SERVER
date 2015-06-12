# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0026_auto_20150612_1158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postcopy',
            name='group',
            field=models.ForeignKey(verbose_name='Group', to='yaga.Group'),
        ),
    ]
