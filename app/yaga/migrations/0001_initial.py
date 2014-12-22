# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import phonenumber_field.modelfields
import yaga.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('request_id', models.CharField(unique=True, max_length=255, verbose_name='Request Id', db_index=True)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(unique=True, max_length=255, verbose_name='Phone Number', db_index=True)),
                ('expire_at', models.DateTimeField(default=yaga.models.expire_at, verbose_name='Expire At', db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
