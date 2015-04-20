# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('cloudflare', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mask',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 20, 15, 22, 11, 180761, tzinfo=utc), verbose_name='Created At', auto_now_add=True),
            preserve_default=False,
        ),
    ]
