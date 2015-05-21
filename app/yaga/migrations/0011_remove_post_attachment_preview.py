# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0010_auto_20150421_1417'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='attachment_preview',
        ),
    ]
