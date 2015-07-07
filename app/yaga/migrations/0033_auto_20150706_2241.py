# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('yaga', '0032_post_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='owner',
            field=models.ForeignKey(related_name='post_owner', verbose_name='Owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='post',
            name='user',
            field=models.ForeignKey(related_name='post_user', verbose_name='User', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='postcopy',
            name='parent',
            field=models.ForeignKey(related_name='post_parent', verbose_name='parent', to='yaga.Post'),
        ),
        migrations.AlterField(
            model_name='postcopy',
            name='post',
            field=models.ForeignKey(related_name='post_post', verbose_name='Post', to='yaga.Post'),
        ),
    ]
