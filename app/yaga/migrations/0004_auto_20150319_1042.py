# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import yaga.models


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0003_post_namer'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='attachment_preview',
            field=models.FileField(upload_to=yaga.models.post_attachment_preview_upload_to, null=True, verbose_name='Attachment Preview', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='attachment',
            field=models.FileField(upload_to=yaga.models.post_attachment_upload_to, null=True, verbose_name='Attachment', blank=True),
            preserve_default=True,
        ),
    ]
