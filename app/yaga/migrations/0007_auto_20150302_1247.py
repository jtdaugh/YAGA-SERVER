# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0006_auto_20150224_1636'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='name_x',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='Name X', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='name_y',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='Name Y', blank=True),
            preserve_default=True,
        ),
    ]
