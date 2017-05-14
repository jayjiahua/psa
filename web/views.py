from django.shortcuts import render, get_object_or_404

from news_spider.models import Channel, News

# Create your views here.

def index(request):
    data = {}
    for channel in Channel.objects.all():
        data[channel.name] = \
            [news.json_data_simple() for news in channel.hottest_news()]
    return render(request, 'index.html', context={"news_group_by_channel": data})

def news_detail(request, news_id):
    news = get_object_or_404(News, news_id=news_id)
    news_data = news.json_data()
    hottest_comments = [comment.json_data() for comment in news.hottest_comment()]
    news_data.update({
        "hottest_comments": hottest_comments,
    })
    similar_news_list = []
    news_list = News.objects.filter(channel_id=news.channel_id)\
        .exclude(news_id=news_id).order_by("-publish_at")
    for n in news_list:
        if not all([n.keywords, news.keywords]):
            continue
        if set(n.keywords.split(";")) & set(news.keywords.split(";")):
            similar_news_list.append(n.json_data())
        if len(similar_news_list) == 10:
            break
    return render(request, 'news_detail.html', context={"news": news_data, "similar_news_list": similar_news_list})

