# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0016_auto_20150521_1932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='name_x',
            field=models.DecimalField(null=True, verbose_name='Name X', max_digits=7, decimal_places=4, blank=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='name_y',
            field=models.DecimalField(null=True, verbose_name='Name Y', max_digits=7, decimal_places=4, blank=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='rotation',
            field=models.DecimalField(null=True, verbose_name='Rotation', max_digits=7, decimal_places=4, blank=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='scale',
            field=models.DecimalField(null=True, verbose_name='Scale', max_digits=7, decimal_places=4, blank=True),
        ),
    ]
