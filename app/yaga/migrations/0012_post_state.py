# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from ..choices import StateChoice


def set_current_state(apps, schema_editor):
    Post = apps.get_model('yaga', 'Post')

    state_choices = StateChoice()

    for post in Post.objects.all():
        if post.ready:
            post.state = state_choices.UPLOADED
        else:
            post.state = state_choices.PENDING

        if post.deleted:
            post.state = state_choices.DELETED

        post.save()


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0011_remove_post_attachment_preview'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='state',
            field=models.PositiveSmallIntegerField(default=0, db_index=True, verbose_name='State', choices=[(0, 'PENDING'), (1, 'UPLOADED'), (10, 'DELETED'), (5, 'READY')]),
        ),
        migrations.RunPython(set_current_state),
    ]
