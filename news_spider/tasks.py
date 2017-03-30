# -*- encoding: utf-8 -*-
#
# 定时任务
#
# 2017/1/2 0002 Jay : Init

import datetime

from django.utils import timezone
from celery.task import task

from news_spider.models import Channel, News, CHANNELS

# TODO: 引入 django-celery 周期任务

@task
def fetch_news():
    for channel in CHANNELS:
        c, _ = Channel.objects.get_or_create(name=channel[0], link=channel[1])
        c.fetch_news()

@task
def fetch_comments():
    yesterday = timezone.now() - datetime.timedelta(days=1)
    news_list = News.objects.filter(publish_at__gt=yesterday).all()
    # news_list = News.objects.all()[:100]
    # news_list = News.objects.filter(news_id="C7J9D7CK002580SL")
    for news in news_list:
        news.fetch_comments()
        # print u"获取评论成功: ", news.comments.count()
