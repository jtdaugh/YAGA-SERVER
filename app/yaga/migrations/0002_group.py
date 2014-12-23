# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yaga', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('members', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Members', db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
