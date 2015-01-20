# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0004_auto_20150115_1447'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 20, 5, 43, 14, 177550, tzinfo=utc), auto_now_add=True, verbose_name='Updated At', db_index=True),
            preserve_default=False,
        ),
    ]
