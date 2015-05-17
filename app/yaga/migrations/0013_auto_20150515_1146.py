# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0012_post_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='post',
            name='ready',
        ),
    ]
