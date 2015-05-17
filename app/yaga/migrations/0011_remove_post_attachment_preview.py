# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.db import models, migrations

logger = logging.getLogger(__name__)


def clean_attachment_previews(apps, schema_editor):
    Post = apps.get_model('yaga', 'Post')

    for post in Post.objects.exclude(
        attachment_preview=''
    ):
        try:
            post.attachment_preview.delete(save=False)
        except Exception as e:
            logger.exception(e)


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0010_auto_20150421_1417'),
    ]

    operations = [
        migrations.RunPython(clean_attachment_previews),
        migrations.RemoveField(
            model_name='post',
            name='attachment_preview',
        ),
    ]
