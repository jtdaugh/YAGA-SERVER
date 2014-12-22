# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0002_auto_20141222_0058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='code',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(unique=True, max_length=255, verbose_name='Phone Number', db_index=True),
            preserve_default=True,
        ),
    ]
