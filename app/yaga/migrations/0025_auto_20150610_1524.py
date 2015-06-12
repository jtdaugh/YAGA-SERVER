# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0024_auto_20150610_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='owner',
            field=models.ForeignKey(related_name='owner', verbose_name='Owner', to=settings.AUTH_USER_MODEL),
        ),
    ]
