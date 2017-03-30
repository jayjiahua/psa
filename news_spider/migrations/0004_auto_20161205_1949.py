# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-05 11:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_spider', '0003_auto_20161205_1945'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='news',
            name='comment_count',
        ),
        migrations.AddField(
            model_name='news',
            name='interaction_count',
            field=models.IntegerField(default=0, verbose_name='\u4e92\u52a8\u603b\u6570'),
        ),
    ]