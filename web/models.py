# coding=utf-8

from __future__ import unicode_literals

from django.db import models

from news_spider.models import Channel
# Create your models here.


class EmailSubscription(models.Model):
    channel = models.ForeignKey(Channel, verbose_name=u"订阅频道", related_name="subscribe_emails")
    email = models.EmailField(u"电子邮箱")
    create_time = models.DateTimeField(u"创建日期", auto_now_add=True)

    def __unicode__(self):
        return self.email

    class Meta:
        verbose_name = u'新闻频道'
        verbose_name_plural = u'新闻频道'