from django.shortcuts import render, get_object_or_404

from news_spider.models import Channel, News

# Create your views here.

def index(request):
    data = {}
    for channel in Channel.objects.all():
        data[channel.name] = \
            [news.json_data_simple() for news in channel.latest_news()]
    return render(request, 'index.html', context={"news_group_by_channel": data})

def news_detail(request, news_id):
    news = get_object_or_404(News, news_id=news_id)
    news_data = news.json_data()
    hottest_comments = [comment.json_data() for comment in news.hottest_comment()]
    news_data.update({
        "hottest_comments": hottest_comments,
    })
    return render(request, 'news_detail.html', context={"news": news_data})