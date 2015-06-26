# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0029_auto_20150618_0935'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='upload_version',
            field=models.PositiveIntegerField(default=0, verbose_name='Upload Client Version'),
        ),
    ]
