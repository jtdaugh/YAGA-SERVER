# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djorm_pgarray.fields


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0005_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='phones',
            field=djorm_pgarray.fields.TextArrayField(dbtype='text', verbose_name='phone'),
            preserve_default=True,
        ),
    ]
