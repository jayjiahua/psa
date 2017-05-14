# -*- encoding: utf-8 -*-
#
# comment
#
# 2016/12/3 0003 Jay : Init

from __future__ import unicode_literals

import requests
import datetime
import time
import json

from django.db import models
from django.utils.safestring import mark_safe
from django.utils import timezone
from bs4 import BeautifulSoup

from nlpir.summary import LJSummary
from nlpir.key_extract import KeyExtract


# Create your models here.

NEWS_URL = "http://temp.163.com/special/00804KVA/%s.js?callback=data_callback"
NEWS_CONTENT_URL = "http://3g.163.com/touch/article/%s/full.html"
COMMENTS_URL = "http://comment.news.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/%s/comments/newList?offset=%d&limit=40&showLevelThreshold=72&headLimit=1&tailLimit=2&callback=getData&ibc=newspc&_=%d"

YAOWEN_NEWS_URL = NEWS_URL % 'cm_yaowen'
SPORT_NEWS_URL = NEWS_URL % 'cm_sports'
GUONEI_NEWS_URL = NEWS_URL % 'cm_guonei'
MONEY_NEWS_URL = NEWS_URL % 'cm_money'
TECH_NEWS_URL = NEWS_URL % 'cm_tech'
GUOJI_NEWS_URL = NEWS_URL % 'cm_guoji'


PROVINCES = (
    (u"未知", u"未知"),
    (u"北京", u"北京市"),
    (u"广东", u"广东省"),
    (u"山东", u"山东省"),
    (u"江苏", u"江苏省"),
    (u"河南", u"河南省"),
    (u"上海", u"上海市"),
    (u"河北", u"河北省"),
    (u"浙江", u"浙江省"),
    (u"香港", u"香港特别行政区"),
    (u"陕西", u"陕西省"),
    (u"湖南", u"湖南省"),
    (u"重庆", u"重庆市"),
    (u"福建", u"福建省"),
    (u"天津", u"天津市"),
    (u"云南", u"云南省"),
    (u"四川", u"四川省"),
    (u"广西", u"广西壮族自治区"),
    (u"安徽", u"安徽省"),
    (u"海南", u"海南省"),
    (u"江西", u"江西省"),
    (u"湖北", u"湖北省"),
    (u"山西", u"山西省"),
    (u"辽宁", u"辽宁省"),
    (u"台湾", u"台湾省"),
    (u"黑龙江", u"黑龙江省"),
    (u"内蒙古", u"内蒙古自治区"),
    (u"澳门", u"澳门特别行政区"),
    (u"贵州", u"贵州省"),
    (u"甘肃", u"甘肃省"),
    (u"青海", u"青海省"),
    (u"新疆", u"新疆维吾尔自治区"),
    (u"西藏", u"西藏自治区"),
    (u"吉林", u"吉林省"),
    (u"宁夏", u"宁夏回族自治区"),
)


CHANNELS = [
    (u'要闻', YAOWEN_NEWS_URL),
    (u'体育', SPORT_NEWS_URL),
    (u'国内', GUONEI_NEWS_URL),
    (u'国际', GUOJI_NEWS_URL),
    (u'财经', MONEY_NEWS_URL),
    (u'科技', TECH_NEWS_URL),
]

class Channel(models.Model):
    name = models.CharField(u"频道名称", max_length=20, unique=True)
    link = models.URLField(u"频道链接", unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'新闻频道'
        verbose_name_plural = u'新闻频道'

    def fetch_news(self):
        session = requests.Session()
        r = session.get(self.link)
        raw_data = r.content[14:-1]
        json_data = json.loads(raw_data, encoding="gbk", strict=False)
        for item in json_data:
            # print item
            if item["newstype"] == "article":
                try:
                    news = News.create_or_update_by_json(self, item)
                    if news:
                        news.fetch_content()
                        news.generate_summary()
                        news.generate_keywords()
                        print self.name, '-', news.title
                except:
                    continue

    def latest_news(self, limit=10):
        return self.news_set.all()[:limit]

    def hottest_news(self, limit=10):
        return self.news_set.order_by("-interaction_count").all()[:limit]


class News(models.Model):
    news_id = models.CharField(u"新闻ID", max_length=20)

    title = models.CharField(u"新闻标题", max_length=256)
    content = models.TextField(u"新闻正文", null=True, blank=True)
    doc_url = models.URLField(u"新闻正文链接")
    img_url = models.URLField(u"新闻图片链接")
    interaction_count = models.IntegerField(u"互动总数", default=0)
    label = models.CharField(u"标签", max_length=256, null=True, blank=True)

    publish_at = models.DateTimeField(u"新闻发布时间")

    create_at = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_at = models.DateTimeField(u"更新时间", auto_now=True)

    channel = models.ForeignKey(Channel, verbose_name=u"所属频道")

    # 分析结果
    summary = models.TextField(u"新闻摘要", null=True, blank=True)
    keywords = models.CharField(u"关键字", max_length=256, null=True, blank=True)


    def json_data(self):
        return {
            "news_id": self.news_id,
            "title": self.title,
            "content": self.content,
            "doc_url": self.doc_url,
            "img_url": self.img_url,
            "interaction_count": self.interaction_count,
            "label": self.label.split(';'),
            # "publish_at": time.mktime(self.publish_at.timetuple()),
            "publish_at": self.publish_at,
            "channel": self.channel.name,
            "summary": self.summary,
            "keywords": self.keywords.split(';') if self.keywords else "",
        }

    def json_data_simple(self):
        return {
            "news_id": self.news_id,
            "title": self.title,
            "img_url": self.img_url,
            "interaction_count": self.interaction_count,
            # "publish_at": time.mktime(self.publish_at.timetuple()),
            "publish_at": self.publish_at,
            "channel": self.channel.name,
        }

    @classmethod
    def create_or_update_by_json(cls, channel, json_data):
        title = json_data["title"]
        doc_url = json_data["docurl"]
        img_url = json_data["imgurl"]
        # interaction_count = json_data["tienum"]
        interaction_count = 0  # 由评论计算
        label = json_data["label"]
        news_id = json_data["docurl"][json_data["docurl"].rfind("/")+1:-5]

        try:
            publish_at = timezone.make_aware(datetime.datetime.strptime(json_data["time"], "%m/%d/%Y %H:%M:%S"))
        except:
            return None

        news, _ = cls.objects.update_or_create(defaults=dict(title=title,
                                                  doc_url=doc_url,
                                                  img_url=img_url,
                                                  interaction_count=interaction_count,
                                                  label=label,
                                                  publish_at=publish_at,
                                                  channel=channel),
                                            news_id=news_id)
        return news

    def fetch_content(self):
        try:
            session = requests.Session()
            r = session.get(NEWS_CONTENT_URL % self.news_id)
            raw_data = r.content[12:-1]
            json_data = json.loads(raw_data, strict=False)
            soup = BeautifulSoup(json_data[self.news_id]["body"], "html.parser", from_encoding='gbk')
            content = ""
            for p in soup.find_all("p"):
                content += p.get_text().strip()
                content += "\n"
            self.content = content
            self.save()
        except Exception, e:
            print self.news_id, e
            self.delete()


    def fetch_comments(self):
        session = requests.Session()
        comment_size = 1
        offset = 0
        limit = 40
        newest_comment = self.comments.order_by("-comment_time").first()
        newest_time = newest_comment.comment_time if newest_comment else None
        is_newest = False
        # TODO: 考虑是否更新之前已经存在的评论（赞同数和反对数会发生变化）
        while offset < comment_size:
            time_stamp = int(time.mktime(datetime.datetime.now().timetuple())) * 1000
            comments_url = COMMENTS_URL % (self.news_id, offset, time_stamp)
            r = session.get(comments_url)
            raw_data = r.content[8:-3]
            json_data = json.loads(raw_data, strict=False)
            try:
                comment_size = json_data["newListSize"]
            except:
                break
            for item in json_data["comments"].values():
                if newest_time:
                    create_time = timezone.make_aware(datetime.datetime.strptime(item["createTime"],
                                                        "%Y-%m-%d %H:%M:%S"))
                    if create_time <= newest_time:
                        is_newest = True
                        break
                try:
                    NewsComment.create_by_json(self, item)
                except:
                    continue

            if is_newest:
                break
            offset += limit

        print u"ok, %s in total" % offset

    def generate_summary(self):
        summary = LJSummary()
        summary.open()
        content = self.content
        result = summary.single_doc(content)
        summary.close()
        self.summary = result
        self.save()

    def generate_keywords(self):
        key_extract = KeyExtract()
        key_extract.open()
        keywords = key_extract.get_keywords(self.content)
        key_extract.close()
        self.keywords = ";".join(keywords)
        self.save()

    def comments_count(self):
        html = '<strong>%d </strong> <a href="/admin/news_spider/newscomment/?news__id__exact=%d"> 查看</a>'
        return mark_safe(html % (self.comments.count(), self.id))

    comments_count.short_description = u"评论数"

    def hottest_comment(self, limit=5):
        return self.comments.order_by("-vote_count")[:limit]

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'新闻条目'
        verbose_name_plural = u'新闻条目'
        ordering = ['-publish_at']


class NewsComment(models.Model):

    comment_id = models.BigIntegerField(u"评论ID")
    comment_time = models.DateTimeField(u"评论时间")
    content = models.TextField(u"评论内容")
    vote_count = models.IntegerField(u"赞成数量", default=0)
    against_count = models.IntegerField(u"反对数量", default=0)
    is_anonymous = models.BooleanField(u"是否匿名")

    # 用户信息
    user_id = models.BigIntegerField(u"用户ID", null=True, blank=True)
    nickname = models.CharField(u"用户名", max_length=64, null=True, blank=True)
    location = models.CharField(u"用户位置", max_length=64, null=True, blank=True)
    province = models.CharField(u"所在省份", max_length=20, default=u"未知", choices=PROVINCES)
    avatar = models.URLField(u"头像链接", null=True, blank=True)

    news = models.ForeignKey(News, verbose_name=u"所属新闻条目", related_name="comments")

    create_at = models.DateTimeField(u"创建时间", auto_now_add=True)

    def __unicode__(self):
        return self.content

    class Meta:
        verbose_name = u'新闻评论'
        verbose_name_plural = u'新闻评论'
        ordering = ["-comment_time"]

    def json_data(self):
        return {
            "is_anonymous": self.is_anonymous,
            "nickname": self.nickname,
            "avatar": self.avatar,
            "comment_time": time.mktime(self.comment_time.timetuple()),
            "content": self.content,
            "vote_count": self.vote_count,
            "against_count": self.against_count,

        }

    @classmethod
    def create_by_json(cls, news, json_data):
        comment_id = json_data["commentId"]
        comment_time = timezone.make_aware(datetime.datetime.strptime(json_data["createTime"], "%Y-%m-%d %H:%M:%S"))
        content = json_data["content"]
        vote_count = json_data["vote"]
        against_count = json_data["against"]
        is_anonymous = json_data["anonymous"]
        user_id = json_data["user"].get("userId", "")
        nickname = json_data["user"].get("nickname", "")
        location = json_data["user"].get("location", "")
        avatar = json_data["user"].get("avatar", "")

        # 匹配所在省市
        province = u"未知"
        for short, name in PROVINCES:
            if short in location:
                province = short
                break


        return cls.objects.get_or_create(defaults=dict(
                                  comment_time=comment_time,
                                  content=content,
                                  vote_count=vote_count,
                                  against_count=against_count,
                                  is_anonymous=is_anonymous,
                                  user_id=user_id,
                                  nickname=nickname,
                                  location=location,
                                  province=province,
                                  avatar=avatar,
                                  news=news), comment_id=comment_id)[0]





#
# def get_segment(news):
#     nlpir = NLPIR()
#     nlpir.open()
#     result = nlpir.segment(news.content)
#     nlpir.close()
#     return result
#
#
# def test_get_sentiment_value():
#     news_list = News.objects.all()[:10]
#     for news in news_list:
#         # print get_sentiment_value(news)
#         # print get_segment(news)
#         # print get_summary(news)
#         print get_word_count_of_comments(news)

