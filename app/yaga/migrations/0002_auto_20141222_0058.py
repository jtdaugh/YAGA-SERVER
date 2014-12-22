# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import yaga.models


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='code',
            name='created_at',
        ),
        migrations.AddField(
            model_name='code',
            name='expire_at',
            field=models.DateTimeField(default=yaga.models.expire_at, verbose_name='Expire At', db_index=True),
            preserve_default=True,
        ),
    ]
