# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20150703_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(max_length=255, null=True, verbose_name='Name', blank=True),
        ),
        migrations.RunSQL('''
            DROP INDEX accounts_user_unique
        '''),
        migrations.RunSQL('''
            CREATE UNIQUE INDEX accounts_user_unique
            ON accounts_user
            USING btree
            (UPPER(name::text))
        '''),
    ]
