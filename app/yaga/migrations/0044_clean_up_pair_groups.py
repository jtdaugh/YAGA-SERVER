# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, IntegrityError, transaction
from django.db.models import Count
from django.forms.models import model_to_dict

from ..choices import ApprovalChoice

import logging

logger = logging.getLogger(__name__)

def clean_up_pair_groups(apps, schema_editor):
    Group = apps.get_model('yaga', 'Group')
    Member = apps.get_model('yaga', 'Member')
    Post = apps.get_model('yaga', 'Post')

    postsModified = 0
    postsFailedToModify = 0

    uniquePairGroupIds = []
    deletedGroupIds = []

    logger.info("Before migration: %d groups", Group.objects.count())
    logger.info("Before migration: %d posts", Post.objects.count())

    for masterGroup in Group.objects.annotate(count=Count('members')).filter(count=2).order_by('-created_at').iterator():
        if (masterGroup.id in deletedGroupIds):
            continue

        uniquePairGroupIds.append(masterGroup.id)

        member_list = list(Member.objects.filter(group=masterGroup))
        logger.info("----------------------------------------------------")
        logger.info("Master group name: %s members: %s, %s", masterGroup.name, str(member_list[0].user.id)[:5], str(member_list[1].user.id)[:5])

        # for key, value in model_to_dict(masterGroup).iteritems():
        #     logger.info("%s: %s", str(key), str(value))

        query = Group.objects.annotate(c=Count('members')).filter(c=2).exclude(id=masterGroup.id)
        # for m in Member.objects.filter(group=masterGroup):
        #     logger.info("Member info:")
        #     for key, value in model_to_dict(m).iteritems():
        #         logger.info("%s: %s", str(key), str(value))
            
        for otherGroup in query.iterator():
            if (otherGroup.id in uniquePairGroupIds):
                continue

            if not (Member.objects.filter(group=otherGroup).filter(user=member_list[0].user).exists() and Member.objects.filter(group=otherGroup).filter(user=member_list[1].user).exists()):
                continue # Exclude groups that dont have identical members

            if otherGroup.id == masterGroup.id:
                continue # Don't want to delete itself. Iedally the exclude above makes this redundant

            deletedGroupIds.append(otherGroup.id)
            
            postsJustMoved = 0
            for post in Post.objects.filter(group=otherGroup):
                post.group = masterGroup
                try:
                    with transaction.atomic():
                        post.save()
                    postsModified += 1
                    postsJustMoved += 1
                except IntegrityError as e:
                    with transaction.atomic():
                        post.delete()
                    postsFailedToModify += 1

            others_member_list = list(Member.objects.filter(group=otherGroup))

            logger.info("%s (%d videos - members: %s, %s) merged into %s", otherGroup.name, postsJustMoved, str(others_member_list[0].user.id)[:5], str(others_member_list[1].user.id)[:5], masterGroup.name)

            with transaction.atomic():
                Member.objects.filter(group=otherGroup).delete()
            with transaction.atomic():
                otherGroup.delete()

    logger.info("Found %d unique pair groups", len(uniquePairGroupIds))
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
