# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-18 12:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('oogiridojo', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='pub_date',
        ),
        migrations.AddField(
            model_name='answer',
            name='creation_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created'),
        ),
    ]
