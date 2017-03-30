# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-26 13:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_analyzer', '0003_auto_20170108_1851'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analysistask',
            name='comment_statistics_json',
        ),
        migrations.AddField(
            model_name='analysistask',
            name='province_statistics_json',
            field=models.TextField(default='null', verbose_name='\u7701\u4efd\u7edf\u8ba1'),
        ),
    ]