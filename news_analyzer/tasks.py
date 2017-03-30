# -*- encoding: utf-8 -*-
#
# comment
#
# 2017/3/26 0026 Jay : Init

import datetime

from django.utils import timezone
from celery.task import task

from news_spider.models import News
from news_analyzer.models import AnalysisTask

@task
def execute_analyse_task():
    yesterday = timezone.now() - datetime.timedelta(days=1)
    news_list = News.objects.filter(publish_at__gt=yesterday).all()
    for news in news_list:
        print u"正在执行分析任务：%s" % news.title
        analyse_task = AnalysisTask.objects.create(news=news)
        analyse_task.execute_task()
        print analyse_task.get_state_display()
