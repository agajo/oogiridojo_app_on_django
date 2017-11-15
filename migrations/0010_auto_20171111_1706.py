# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-11 08:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('oogiridojo', '0009_auto_20171031_1807'),
    ]

    operations = [
        migrations.CreateModel(
            name='Monkasei',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
            ],
        ),
        migrations.AddField(
            model_name='answer',
            name='monkasei',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='oogiridojo.Monkasei'),
            preserve_default=False,
        ),
    ]