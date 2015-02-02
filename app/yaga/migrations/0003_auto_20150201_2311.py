# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yaga', '0002_remove_post_notified'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='creator',
            field=models.ForeignKey(related_name='creator', verbose_name='Creator', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='member',
            name='user',
            field=models.ForeignKey(related_name='user', verbose_name='User', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
