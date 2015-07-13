from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import uuid

from django.core.management.base import BaseCommand

from ...models import Group


class Command(
    BaseCommand
):
    help = 'Remove ALL members from group'

    def add_arguments(self, parser):
        parser.add_argument('group_id')

    def handle(self, *args, **options):
        try:
            group_id = uuid.UUID(options['group_id'])
        except Exception:
            self.stderr.write('Invalid UUID {group_id}'.format(
                group_id=group_id
            ))
            return

        try:
            group = Group.objects.get(
                pk=group_id
            )
        except Group.DoesNotExist:
            self.stderr.write('Group {group_id} not found'.format(
                group_id=group_id
            ))
            return

        self.stdout.write('Removing {count} members from {group}'.format(
            count=group.member_set.count(),
            group=group.pk
        ))

        for member in group.member_set.all():
            self.stdout.write('Removing {member}'.format(
                member=member.user.get_username()
            ))
            member.delete()
