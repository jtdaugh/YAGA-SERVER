# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.models import Count

from ..choices import ApprovalChoice

import logging

logger = logging.getLogger(__name__)

def clean_up_pair_groups(apps, schema_editor):
    Group = apps.get_model('yaga', 'Group')
    Member = apps.get_model('yaga', 'Member')
    Post = apps.get_model('yaga', 'Post')

    uniquePairGroups = 0
    postsModified = 0

    deletedGroupIds = []

    for group in Group.objects.annotate(count=Count('members')).filter(count=2):
        if (group.id in deletedGroupIds):
            continue
        
        uniquePairGroups += 1
        
        query = Group.objects.exclude(id=group.id)
        for member in group.members.all():
            query = query.filter(members=member)
        
        for otherGroup in query:
            deletedGroupIds.append(otherGroup.id)
            for post in Post.objects.filter(group=otherGroup):
                postsModified += 1
                post.group = group
                post.save()
            Member.objects.filter(group=otherGroup).delete()
            otherGroup.delete()

    logger.info("Found %d unique pair groups", uniquePairGroups)
    logger.info("Deleted %d groups", len(deletedGroupIds))
    logger.info("Modified %d posts", postsModified)


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0043_delete_non_active_memberships'),
    ]

    operations = [
        migrations.RunPython(clean_up_pair_groups),
    ]
