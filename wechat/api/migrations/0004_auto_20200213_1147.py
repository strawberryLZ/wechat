# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-02-13 03:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20200210_1127'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userinfo',
            old_name='blance',
            new_name='balance',
        ),
    ]
