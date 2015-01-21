# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0007_post_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 21, 3, 15, 37, 47590, tzinfo=utc), auto_now=True, verbose_name='Updated At', db_index=True),
            preserve_default=False,
        ),
    ]
