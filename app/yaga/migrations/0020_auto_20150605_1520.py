# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djorm_pgarray.fields


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0019_auto_20150605_0101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='phones',
            field=djorm_pgarray.fields.ArrayField(dbtype='character varying(255)', verbose_name='Phones', blank=False),
        ),
    ]
