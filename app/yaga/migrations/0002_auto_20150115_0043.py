# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import app.model_fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yaga', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', app.model_fields.UUIDField(max_length=32, serialize=False, editable=False, primary_key=True, blank=True)),
                ('vendor', models.PositiveSmallIntegerField(db_index=True, verbose_name='Vendor', choices=[(0, 'IOS'), (1, 'ANDROID')])),
                ('token', models.CharField(max_length=255, verbose_name='Request Id', db_index=True)),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Device',
                'verbose_name_plural': 'Devices',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='device',
            unique_together=set([('vendor', 'token')]),
        ),
        migrations.AlterField(
            model_name='post',
            name='mime',
            field=models.CharField(db_index=True, max_length=255, null=True, verbose_name='Mime', blank=True),
            preserve_default=True,
        ),
    ]
