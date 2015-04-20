# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.model_fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mask',
            fields=[
                ('id', app.model_fields.UUIDField(max_length=32, serialize=False, editable=False, primary_key=True, blank=True)),
                ('value', models.CharField(unique=True, max_length=255, verbose_name='Mask')),
            ],
            options={
                'verbose_name': 'Mask',
                'verbose_name_plural': 'Masks',
            },
            bases=(models.Model,),
        ),
    ]
