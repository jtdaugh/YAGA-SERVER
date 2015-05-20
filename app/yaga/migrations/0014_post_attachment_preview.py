# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import yaga.models


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0013_auto_20150515_1146'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='attachment_preview',
            field=models.FileField(default='', upload_to=yaga.models.post_attachment_preview_upload_to, verbose_name='Attachment Preview', blank=True),
        ),
    ]
