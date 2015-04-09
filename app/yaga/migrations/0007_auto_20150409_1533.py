# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import yaga.models


def update_attachment(apps, schema_editor):
    Post = apps.get_model('yaga', 'Post')

    for post in Post.objects.filter(
        attachment__isnull=True
    ):
        post.attachment = ''
        post.save()


def update_attachment_preview(apps, schema_editor):
    Post = apps.get_model('yaga', 'Post')

    for post in Post.objects.filter(
        attachment_preview__isnull=True
    ):
        post.attachment_preview = ''
        post.save()


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0006_auto_20150324_1507'),
    ]

    operations = [
        migrations.RunPython(update_attachment),
        migrations.AlterField(
            model_name='post',
            name='attachment',
            field=models.FileField(default='', upload_to=yaga.models.post_attachment_upload_to, verbose_name='Attachment', blank=True),
            preserve_default=True,
        ),
        migrations.RunPython(update_attachment_preview),
        migrations.AlterField(
            model_name='post',
            name='attachment_preview',
            field=models.FileField(default='', upload_to=yaga.models.post_attachment_preview_upload_to, verbose_name='Attachment Preview', blank=True),
            preserve_default=True,
        ),
    ]
