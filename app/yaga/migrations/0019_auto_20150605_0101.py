# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def cleanup_contacts(apps, schema_editor):
    Contact = apps.get_model('yaga', 'Contact')

    for contact in Contact.objects.all():
        phones = set(contact.phones)

        try:
            phones.remove(str(contact.user.phone))
        except KeyError:
            pass

        phones = list(phones)

        if phones != contact.phones:
            contact.phones = phones
            contact.save()


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0018_post_miscellaneous'),
    ]

    operations = [
        migrations.RunPython(cleanup_contacts),
    ]
