# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0008_group_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='locale',
            field=models.CharField(default='en', max_length=2, verbose_name='Locale'),
            preserve_default=False,
        ),
    ]
