# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0040_alter_follow'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='follow',
        ),
    ]
