# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from ..choices import StatusChoice

import logging

logger = logging.getLogger(__name__)

# Delete all member rows where the status is PENDING, LEFT, or FOLLOWER
def delete_non_active_memberships(apps, schema_editor):
    Member = apps.get_model('yaga', 'Member')
    status_choices = StatusChoice()

    count = 0
    for member in Member.objects.exclude(status=status_choices.MEMBER):
        member.delete()
        count += 1

    logger.info("deleted %d memberships", count);



class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0042_delete_public_groups'),
    ]

    operations = [
        migrations.RunPython(delete_non_active_memberships),
    ]
