# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0033_auto_20150706_2241'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'verbose_name': 'Post', 'verbose_name_plural': 'Posts', 'permissions': (('view_post', 'Can view Post'), ('approve_post', 'Can approve Post'))},
        ),
    ]
