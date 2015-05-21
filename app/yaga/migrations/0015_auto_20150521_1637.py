# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from ..choices import StateChoice
from ..tasks import TranscodingTask


def transcode(apps, schema_editor):
    Post = apps.get_model('yaga', 'Post')

    state_choices = StateChoice()

    for post in Post.objects.filter(
        state=state_choices.UPLOADED
    ):
        TranscodingTask().delay(post.pk)


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0014_post_attachment_preview'),
    ]

    operations = [
        migrations.RunPython(transcode),
    ]
