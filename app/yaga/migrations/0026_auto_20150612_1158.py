# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def wipe_copies(apps, schema_editor):
    PostCopy = apps.get_model('yaga', 'PostCopy')

    for copy in PostCopy.objects.all():
        copy.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0025_auto_20150610_1524'),
    ]

    operations = [
        migrations.RunPython(wipe_copies),
        migrations.AddField(
            model_name='postcopy',
            name='group',
            field=models.ForeignKey(default=None, verbose_name='Group', to='yaga.Group'),
        ),
        migrations.AlterUniqueTogether(
            name='postcopy',
            unique_together=set([('parent', 'group')]),
        ),
    ]
