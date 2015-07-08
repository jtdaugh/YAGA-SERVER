# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0034_auto_20150707_0735'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='owner',
        ),
    ]
