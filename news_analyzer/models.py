# -*- encoding: utf-8 -*-
#
# 定时任务
#
# 2017/1/2 0002 Jay : Init

from __future__ import unicode_literals

import json
import traceback
import datetime
import time


from django.db import models

from news_spider.models import News, PROVINCES
from nlpir.doc_extractor import DocExtractor
from nlpir.sentiment_analysis import LJSentimentAnalysis
from nlpir.nlpir_ictclas import NLPIR
from nlpir.key_extract import KeyExtract

# Create your models here.


class AnalysisState:
    WAITING = "waiting"
    RUNNING = "running"
    SUCCESSFUL = "successful"
    FAILED = "failed"

class AnalysisTask(models.Model):
    """
    随时间变化的新闻分析结果
    """

    ANALYSIS_STATE = (
        (AnalysisState.WAITING, u"等待分析"),
        (AnalysisState.RUNNING, u"正在分析"),
        (AnalysisState.SUCCESSFUL, u"分析成功"),
        (AnalysisState.FAILED, u"分析失败"),
    )

    news = models.ForeignKey(News, related_name="analysis_results",
                             verbose_name=u"所属新闻")

    # 分析结果
    province_statistics_json = models.TextField(u"省份统计", default="null")
    word_count_json = models.TextField(u"词频统计", default="null")
    sentiment_value_json = models.TextField(u"情感值统计", default="null")
    keyword_statistics_json = models.TextField(u"关键词统计", default="null")
    interaction_count = models.IntegerField(u"互动总数", default=0)

    create_time = models.DateTimeField(u"任务创建时间", auto_now_add=True)
    start_time = models.DateTimeField(u"分析开始时间", null=True)
    end_time = models.DateTimeField(u"分析结束时间", null=True)

    state = models.CharField(u"分析状态", max_length=20, choices=ANALYSIS_STATE,
                             default=AnalysisState.WAITING)
    ex_data = models.TextField(u"额外信息", null=True)

    @property
    def province_statistics(self):
        return json.loads(self.province_statistics_json)

    @province_statistics.setter
    def province_statistics(self, value):
        self.province_statistics_json = json.dumps(value)

    @property
    def keyword_statistics(self):
        return json.loads(self.keyword_statistics_json)

    @keyword_statistics.setter
    def keyword_statistics(self, value):
        self.keyword_statistics_json = json.dumps(value)

    @property
    def word_count(self):
        return json.loads(self.word_count_json)

    @word_count.setter
    def word_count(self, value):
        self.word_count_json = json.dumps(value)


    @property
    def sentiment_value(self):
        return json.loads(self.sentiment_value_json)

    @sentiment_value.setter
    def sentiment_value(self, value):
        self.sentiment_value_json = json.dumps(value)




    def generate_sentiment_value(self):
        doc_extractor = DocExtractor()
        doc_extractor.open()
        sentiment_analysis = LJSentimentAnalysis()
        sentiment_analysis.open()
        positive = 0
        negative = 0
        neutral = 0
        emotions = {
            'EMOTION_GOOD': 0,
            'EMOTION_ANGER': 0,
            'EMOTION_HAPPY': 0,
            'EMOTION_FEAR': 0,
            'EMOTION_SURPRISE': 0,
            'EMOTION_EVIL': 0,
            'EMOTION_SORROW': 0,
        }

        # 省份字典
        province_statistics = {
            province[0]: {
                "comment_count": 0,
                "positive": 0,
                "neutral": 0,
                "negative": 0,
                "emotions": {
                    'EMOTION_GOOD': 0,
                    'EMOTION_ANGER': 0,
                    'EMOTION_HAPPY': 0,
                    'EMOTION_FEAR': 0,
                    'EMOTION_SURPRISE': 0,
                    'EMOTION_EVIL': 0,
                    'EMOTION_SORROW': 0,
                }
            } for province in PROVINCES}

        for comment in self.news.comments.all():
            val = doc_extractor.get_sentiment_value(comment.content)
            vote_count = comment.vote_count
            against_count = comment.against_count

            # 计算正负面数值
            # 评定方法：
            #      | 正面 | 负面 | 中立
            # -----+------+-----+------
            # 赞同  | 正面 | 负面 | 中立
            # -----+------+-----+------
            # 反对  | 负面 | 正面 | 中立
            # -------------------------
            single_positive = 0
            single_negative = 0
            single_neutral = 0
            if val > 0:
                # 反对正面评论的被记为负面值
                single_positive = 1 + vote_count
                single_negative = against_count
            elif val < 0:
                # 反对负面评论的被记为正面值
                single_negative = 1 + vote_count
                single_positive = against_count
            else:
                # 无论赞同还是反对中性评论都只记为中性值
                single_neutral = 1 + vote_count + against_count

            # 更新总态度数值
            positive += single_positive
            negative += single_negative
            neutral += single_neutral

            #　更新各省份态度数值
            province = comment.province
            province_statistics[province]["comment_count"] += 1
            province_statistics[province]["positive"] += single_positive
            province_statistics[province]["negative"] += single_negative
            province_statistics[province]["neutral"] += single_neutral

            # 更新情感值
            e = sentiment_analysis.get_result(comment.content)
            for k, v in e.items():
                # 更新省份情感值
                province_statistics[province]["emotions"][k] += v

                # 更新总情感值
                emotions[k] += v

        doc_extractor.close()
        sentiment_analysis.close()

        self.sentiment_value = {
            "polarity": {
                "positive": positive,
                "neutral": neutral,
                "negative": negative,
            },
            "emotions": emotions,
        }
        self.province_statistics = province_statistics
        self.save()

    def generate_word_count_and_keywords(self):
        nlpir = NLPIR()
        nlpir.open()

        key_extract = KeyExtract()
        key_extract.open()

        comments = []

        for comment in self.news.comments.all():
            comments.append(comment.content)

        content = u"\n".join(comments)

        word_count_ranking = nlpir.segment_and_count(content)
        keywords = key_extract.get_keywords(content, 100, True)

        nlpir.close()
        key_extract.close()

        self.word_count = [{
            "word": item[0],
            "pos": item[1],
            "count": item[2]
        } for item in word_count_ranking]

        self.keyword_statistics = [{
            "keyword": item[0],
            "rank": item[1]
        } for item in keywords]

        self.save()

    def generate_word_count_of_comments(self):
        nlpir = NLPIR()
        nlpir.open()
        word_count_dict = {}
        for comment in self.news.comments.all():
            try:
                single_word_count = nlpir.segment_and_count(comment.content)
            except:
                continue
            for item in single_word_count:
                # TODO: 只保存特定某些词性的词语，如标点符号无需保存
                pos = item[1]  # 词性

                if not word_count_dict.has_key(item[0]):
                    word_count_dict[item[0]] = {
                        "pos": pos,
                        "count": item[2]
                    }
                else:
                    new_word_count = word_count_dict[item[0]]["count"] + item[2]
                    word_count_dict.update({
                        item[0]: {
                            "pos": pos,
                            "count": new_word_count
                        }
                    })
        nlpir.close()
        word_count_ranking = sorted(word_count_dict.items(),
                                    key=lambda d: -d[1]["count"])
        # TODO: 只保存排在前N位的词频
        self.word_count = [{
            "word": item[0],
            "pos": item[1]["pos"],
            "count": item[1]["count"]
        } for item in word_count_ranking]

        self.save()

    # def generate_comment_statistics(self):
    #     count_by_province = self.news.comments.order_by('province')\
    #         .values('province')\
    #         .annotate(comment_count=models.Count("comment_id")).all()
    #     result = {
    #         "total": self.news.comments.count(),
    #         "details": list(count_by_province)
    #     }
    #     self.comment_statistics = result
    #     self.save()

    def generate_interaction_count(self):
        interaction_count = 0
        for comment in self.news.comments.all():
            interaction_count += 1 + comment.vote_count + comment.against_count

        self.interaction_count = interaction_count
        self.save()

        self.news.interaction_count = interaction_count
        self.news.save()

    def execute_task(self):
        self.start_time = datetime.datetime.now()
        self.state = AnalysisState.RUNNING
        self.save()

        try:
            self.generate_word_count_and_keywords()
            self.generate_sentiment_value()
            self.generate_interaction_count()

            self.end_time = datetime.datetime.now()
            self.state = AnalysisState.SUCCESSFUL
            self.save()

        except:
            self.end_time = datetime.datetime.now()
            self.state = AnalysisState.FAILED
            self.ex_data = traceback.format_exc()
            self.save()

    def json_data(self):
        return {
            "province_statistics": self.province_statistics,
            "word_count": self.word_count[:100],
            "keywords": self.keyword_statistics,
            "sentiment_value": self.sentiment_value,
            "create_time": time.mktime(self.create_time.timetuple()),
            "interaction_count": self.interaction_count,
        }

    def __unicode__(self):
        return self.news.title


    class Meta:
        verbose_name = u'新闻分析任务'
        verbose_name_plural = u'新闻分析任务'
        ordering = ['-create_time']



