# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('request_id', models.CharField(unique=True, max_length=255, verbose_name='Request Id', db_index=True)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=255, verbose_name='Phone Number', db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date joined', db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
