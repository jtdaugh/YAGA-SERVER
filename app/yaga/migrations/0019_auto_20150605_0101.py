# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def remove_self_from_contacts(apps, schema_editor):
    Contact = apps.get_model('yaga', 'Contact')

    for contact in Contact.objects.all():
        if str(contact.user.phone) in contact.phones:
            contact.phones.remove(str(contact.user.phone))
            contact.save()


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0018_post_miscellaneous'),
    ]

    operations = [
        migrations.RunPython(remove_self_from_contacts),
    ]
