# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, IntegrityError, transaction
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
    postsFailedToModify = 0

    deletedGroupIds = []

    logger.info("Before migration: %d groups", Group.objects.count())
    logger.info("Before migration: %d posts", Post.objects.count())

    for group in Group.objects.annotate(count=Count('members')).filter(count=2):
        if (group.id in deletedGroupIds):
            continue
        
        uniquePairGroups += 1
        
        query = Group.objects.annotate(c=Count('members')).filter(c=2).exclude(id=group.id)
        
        # for m in group.members.all():
        #     query = query.filter(member__user=m)
        
        member_list = list(group.members.all())

        for otherGroup in query:
            if not (Member.objects.filter(group=otherGroup).filter(user=member_list[0]).exists() && Member.objects.filter(group=otherGroup).filter(user=member_list[1]).exists()):
                break

            deletedGroupIds.append(otherGroup.id)
            for post in Post.objects.filter(group=otherGroup):
                post.group = group
                try:
                    with transaction.atomic():
                        post.save()
                    postsModified += 1
                except IntegrityError as e:
                    with transaction.atomic():
                        post.delete()
                    postsFailedToModify += 1

            Member.objects.filter(group=otherGroup).delete()
            otherGroup.delete()

    logger.info("Found %d unique pair groups", uniquePairGroups)
    logger.info("Deleted %d groups", len(deletedGroupIds))
    logger.info("Modified %d posts", postsModified)
    logger.info("Failed to modify, thus deleted %d posts", postsFailedToModify)

class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0043_delete_non_active_memberships'),
    ]

    operations = [
        migrations.RunPython(clean_up_pair_groups),
    ]
