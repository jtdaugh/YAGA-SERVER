# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from ..choices import ApprovalChoice

import logging

logger = logging.getLogger(__name__)

def delete_public_groups(apps, schema_editor):
    Group = apps.get_model('yaga', 'Group')
    Member = apps.get_model('yaga', 'Member')

    count = 0;
    
    for groupToDelete in Group.objects.filter(private=False):
        Member.objects.filter(group=groupToDelete).delete()
        groupToDelete.delete()
        count += 1
    
    logger.info("deleted %d public groups", count);


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0041_remove_member_follow'),
    ]

    operations = [
        migrations.RunPython(delete_public_groups),
    ]
