# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='name',
            field=models.CharField(null=True, max_length=255, blank=True, unique=True, verbose_name='Name', db_index=True),
            preserve_default=True,
        ),
    ]
