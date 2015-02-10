# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djorm_pgarray.fields
import app.model_fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yaga', '0004_auto_20150204_2207'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', app.model_fields.UUIDField(max_length=32, serialize=False, editable=False, primary_key=True, blank=True)),
                ('phones', djorm_pgarray.fields.ArrayField(dbtype='varchar(255)', verbose_name='phones')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('user', models.OneToOneField(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Contact',
                'verbose_name_plural': 'Contacts',
            },
            bases=(models.Model,),
        ),
        migrations.RunSQL('''
            CREATE INDEX yaga_contact_gin on "yaga_contact" USING GIN ("phones");
        ''')
    ]
