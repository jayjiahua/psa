# coding=utf-8

from __future__ import unicode_literals
from ctypes import (c_bool, c_char, c_char_p, c_double, c_int, c_uint,
                    c_ulong, c_void_p, cdll, POINTER, Structure)

from base import BaseNlpirSDK

import logging
import os
import sys

logger = logging.getLogger('nlpir.LJSentimentAnalysis')


LIB_NAME = 'LJSentimentAnalysis'
SHORT_NAME = 'LJST'

class LJSentimentAnalysis(BaseNlpirSDK):

    def __init__(self):
        BaseNlpirSDK.__init__(self, LIB_NAME, SHORT_NAME)

        # C函数定义
        # Get the exported NLPIR API functions.
        self.GetParagraphSent = self.get_func('LJST_GetParagraphSent', [c_char_p, c_char_p], c_bool)
        # self.ImportUserDict = self.get_func('LJST_ImportUserDict', [c_char_p, c_bool], c_int)

    def get_result(self, s):
        s = self._decode(s)
        logger.debug("Get the sentiment of the text: %s." % s)

        result = c_char_p('\0'*10000)  # 必须填至少16个字符才不至于程序崩溃，我也不知道为什么...

        is_success = self.GetParagraphSent(self._encode(s), result)

        if is_success:
            result = self._decode(result.value)
            logger.debug("The sentiment of the text is: %s." % result)
            emotions = result.strip().split("\n")
            ret = {}
            for emotion in emotions:
                key, val = emotion.split("/")
                ret[key] = int(val)
            return ret
        else:
            return None

def test():
    sentiment_analysis = LJSentimentAnalysis()
    sentiment_analysis.open()
    result = sentiment_analysis.get_result("""
参考消息网12月6日报道 港媒称，中国官员在广东的一个环保论坛上承认，中国在几乎所有空气污染类别中都排在世界首位，包括二氧化硫和一氧化氮，碳排放也是如此。
据香港《南华早报》网站12月6日报道，专家还指出，京津冀地区是全世界污染最严重的地区之一。
媒体援引环境保护部环境规划院总工程师王金南的话说，要在明年之前实现中国减少污染的目标，需要投资1.75万亿元，但投资缺口给这一行动带来了巨大障碍。
在近日举行的“2016中国环保上市公司峰会”上，王金南说：“几乎所有的污染物排放指标和二氧化碳排放指标在全世界排放量都是第一，整个大气的压力前所未有。”
他说，在京津冀区域有大量的污染物排放，直接的结果是导致PM2.5上升，全国来看，最近几十年能见度平均下降50公里左右，京津冀地区已经成为全世界污染最严重的地区之一。
工业和信息化部官员雷文说，近10年来，国家在节能减排、环境保护方面投入巨大的人力物力，也取得明显成效，但总体来看，高投入、高排放、高污染的生产模式并没有得到最根本的改变。
中国的工业总产值在2011年超过美国，成为世界第一，但是工厂不严格执行环保标准成为污染的主要原因。
雷文说，虽然中国大部分火电站都安装了先进的过滤装置，但工厂的燃煤未受到很好监管，它们继续向大气中排放污染物。
工信部下属的赛迪研究院说，2015年非电工业领域耗煤量约占全国煤炭消费总量的46%，这些工业炉窑的环保标准没有火电行业严格。
王金南还说，环保投入不足仍是一个突出问题。中央政府承诺环保投入占GDP的比例为1.5%左右，但近几年真正投入环境保护的没有那么高，大致只有1%左右。

作者：殷欣

    """)
    print result
    sentiment_analysis.close()


if __name__ == '__main__':
    test()
