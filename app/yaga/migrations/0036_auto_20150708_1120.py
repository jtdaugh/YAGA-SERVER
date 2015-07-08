# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def ensure_humanity(apps, schema_editor):
    Group = apps.get_model('yaga', 'Group')

    humanity = Group.objects.get_or_create(
        private=False,
        name='Humanity'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0035_remove_post_owner'),
    ]

    operations = [
        migrations.RunPython(ensure_humanity)
    ]