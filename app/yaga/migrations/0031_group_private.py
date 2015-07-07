# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0030_post_upload_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='private',
            field=models.BooleanField(default=True, db_index=True, verbose_name='Private'),
        ),
    ]
