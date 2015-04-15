# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0008_auto_20150415_1317'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='post',
            unique_together=set([('checksum', 'group')]),
        ),
    ]
