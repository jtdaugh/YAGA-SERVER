# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0002_auto_20141231_0824'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='name',
            field=models.CharField(max_length=255, null=True, verbose_name='Name', blank=True),
            preserve_default=True,
        ),
    ]
