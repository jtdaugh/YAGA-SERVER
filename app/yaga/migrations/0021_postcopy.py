# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.model_fields


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0020_auto_20150605_1520'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostCopy',
            fields=[
                ('id', app.model_fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('parent', models.ForeignKey(related_name='parent', verbose_name='User', to='yaga.Post')),
                ('post', models.ForeignKey(related_name='post', verbose_name='User', to='yaga.Post')),
            ],
            options={
                'verbose_name': 'Post Copy',
                'verbose_name_plural': 'Post Copy',
            },
        ),
    ]
