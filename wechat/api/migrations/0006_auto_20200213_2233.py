# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-02-13 14:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20200213_2232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='balance',
            field=models.IntegerField(default=0, verbose_name='余额'),
        ),
    ]
