# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import yaga.models


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0015_auto_20150521_1637'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Updated At', auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='post',
            name='attachment_preview',
            field=models.FileField(default='', upload_to=yaga.models.post_attachment_server_preview_upload_to, verbose_name='Attachment Preview', blank=True),
        ),
    ]
