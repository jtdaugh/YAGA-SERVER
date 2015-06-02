# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0017_auto_20150602_2028'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='miscellaneous',
            field=models.CharField(max_length=255, null=True, verbose_name='Miscellaneous', blank=True),
        ),
    ]
