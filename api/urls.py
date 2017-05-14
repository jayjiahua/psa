# -*- encoding: utf-8 -*-
#
# comment
#
# 2017/1/15 0015 Jay : Init


from django.conf.urls import url
from api.views import (channels, latest_news, news, news_detail,
                    news_analysis_data, search_news, news_time_data)

urlpatterns = [
    url(r'^channels/$', channels),
    url(r'^latest_news/$', latest_news),
    url(r'^news/$', news),
    url(r'^news/(?P<news_id>\w+)/$', news_detail),
    url(r'^news/(?P<news_id>\w+)/analysis_data/$', news_analysis_data),
    url(r'^search_news/$', search_news),
    url(r'^news_time_data/(?P<news_id>\w+)/$', news_time_data),
]