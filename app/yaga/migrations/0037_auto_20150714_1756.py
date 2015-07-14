# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0036_auto_20150708_1120'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name': 'Group', 'verbose_name_plural': 'Groups', 'permissions': (('view_group', 'Can view Group'), ('wipe_group', 'Can wipe Group'))},
        ),
    ]
