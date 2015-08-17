# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0039_auto_20150817_0951'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='follow',
        ),
    ]
