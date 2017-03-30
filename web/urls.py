# -*- encoding: utf-8 -*-
#
# comment
#
# 2017/3/13 0013 Jay : Init

from django.conf.urls import url
from web.views import index, news_detail

urlpatterns = [
    url(r'^$', index),
    url(r'^news/(?P<news_id>\w+)/$', news_detail)
]