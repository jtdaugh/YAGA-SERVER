# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils import timezone


def update_verified_at(apps, schema_editor):
    User = apps.get_model('accounts', 'User')

    for user in User.objects.filter(
        verified=True
    ):
        user.verified_at = timezone.now()
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20150324_1240'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='verified_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='Verified At', blank=True),
            preserve_default=True,
        ),
        migrations.RunPython(update_verified_at)
    ]
