# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0023_auto_20150610_1520'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='postcopy',
            options={'verbose_name': 'Post Copy', 'verbose_name_plural': 'Post Copies'},
        ),
        migrations.AlterField(
            model_name='postcopy',
            name='parent',
            field=models.ForeignKey(related_name='parent', verbose_name='parent', to='yaga.Post'),
        ),
        migrations.AlterField(
            model_name='postcopy',
            name='post',
            field=models.ForeignKey(related_name='post', verbose_name='Post', to='yaga.Post'),
        ),
    ]
