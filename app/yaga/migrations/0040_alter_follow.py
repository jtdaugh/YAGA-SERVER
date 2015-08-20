# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0039_alter_group_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='follow',
            field=models.BooleanField(default=False, db_index=True, verbose_name='Follow'),
        ),
    ]
