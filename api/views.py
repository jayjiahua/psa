from django.shortcuts import render, get_object_or_404

from news_spider.models import Channel, News
from .utils import render_json
# Create your views here.

def channels(request):
    channels = list(Channel.objects.values("name").all())
    return render_json(data=channels)

def latest_news(request):
    data = {}
    for channel in Channel.objects.all():
        data[channel.name] = \
            [news.json_data_simple() for news in channel.latest_news()]
    return render_json(data=data)

def news(request):
    channel_name = request.GET.get("channel")

    try:
        limit = int(request.GET.get("limit"))
    except:
        limit = 10

    try:
        offset = int(request.GET.get("offset"))
    except:
        offset = 0

    if channel_name == None:
        query_set = News.objects
    else:
        try:
            channel = Channel.objects.get(name=channel_name)
            query_set = channel.news_set
        except Channel.DoesNotExist:
            return render_json(data=[])

    total_count = query_set.count()

    news_list = query_set.all()[offset:offset+limit]

    ret_data = [news.json_data_simple() for news in news_list]
    return render_json(data=ret_data, extra_params={"total_count": total_count})

def news_detail(request, news_id):
    news = get_object_or_404(News, news_id=news_id)
    ret_data = news.json_data()
    hottest_comments = [comment.json_data() for comment in news.hottest_comment()]
    ret_data.update({
        "hottest_comments": hottest_comments,
    })
    return render_json(data=ret_data)

def news_analysis_data(request, news_id):
    news = get_object_or_404(News, news_id=news_id)
    analysis_result = news.analysis_results.first()
    if analysis_result:
        ret_data = analysis_result.json_data()
    else:
        ret_data = None
    return render_json(data=ret_data)


