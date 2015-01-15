# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0002_auto_20150115_0043'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='notified',
            field=models.BooleanField(default=False, db_index=True, verbose_name='Notified'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='device',
            name='vendor',
            field=models.PositiveSmallIntegerField(db_index=True, verbose_name='Vendor', choices=[(0, 'IOS'), (1, 'ADNDROID')]),
            preserve_default=True,
        ),
    ]
