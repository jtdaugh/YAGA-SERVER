# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from ..choices import ApprovalChoice

def clean_up_pair_groups(apps, schema_editor):
    Group = apps.get_model('yaga', 'Group')
    Member = apps.get_model('yaga', 'Member')

    for group in Group.objects.all():
        if group.active_member_count() != 2:
            continue
        else
            for otherGroup in Group.objects.filter(id != group.id, members=group.members):
                if otherGroup.active_member_count() != 2:
                    continue
                else
                    


        # If # of active members != 2, continue
        # If 2 active members:
            # For each group with matching members
                # For each post in group:
                    # Update group for post
                # Delete all Member objects for group
                # Delete group


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0042_delete_public_groups.py'),
    ]

    operations = [
        migrations.RunPython(clean_up_pair_groups),
    ]
