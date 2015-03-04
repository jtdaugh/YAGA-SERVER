# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0007_auto_20150302_1247'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='font',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='Font', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='rotation',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='Rotation', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='scale',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='Scale', blank=True),
            preserve_default=True,
        ),
    ]
