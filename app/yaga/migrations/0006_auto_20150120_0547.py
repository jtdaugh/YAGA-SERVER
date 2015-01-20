# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0005_post_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated At', db_index=True),
            preserve_default=True,
        ),
    ]
