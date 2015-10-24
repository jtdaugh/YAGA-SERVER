# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from ..choices import ApprovalChoice

def delete_public_groups(apps, schema_editor):
    Group = apps.get_model('yaga', 'Group')
    Member = apps.get_model('yaga', 'Member')

    for groupToDelete in Group.objects.filter(private=False):
        Member.objects.filter(group=groupToDelete).delete()
        groupToDelete.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0041_remove_member_follow'),
    ]

    operations = [
        migrations.RunPython(delete_public_groups),
    ]
