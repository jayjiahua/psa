# coding=utf-8

from __future__ import unicode_literals
from ctypes import (c_bool, c_char, c_char_p, c_double, c_int, c_uint,
                    c_ulong, c_void_p, cdll, POINTER, Structure)

from base import BaseNlpirSDK

import logging
import os
import sys

logger = logging.getLogger('nlpir.KeyExtract')


LIB_NAME = 'KeyExtract'
SHORT_NAME = 'KeyExtract'

class KeyExtract(BaseNlpirSDK):

    def __init__(self):
        BaseNlpirSDK.__init__(self, LIB_NAME, SHORT_NAME)

        # C函数定义
        # Get the exported NLPIR API functions.
        self.GetKeyWords = self.get_func('KeyExtract_GetKeyWords', [c_char_p, c_int, c_bool], c_char_p)

    def get_keywords(self, s, max_key_limit=10, weight_out=False):
        s = self._decode(s)
        logger.debug("Get the keywords of the text: %s." % s)

        result = self.GetKeyWords(self._encode(s), max_key_limit, weight_out)
        result = self._decode(result)

        logger.debug("The keywords of the text is: %s." % result)

        fresult = result.strip('#').split('#') if result else []
        if weight_out:
            weights, words = [], []
            for w in fresult:
                result = w.split('/')
                word, weight = result[0], result[2]
                weight = float(weight)
                weights.append(weight or 0.0)
                words.append(word)
            fresult = zip(words, weights)

        logger.debug("Key words formatted: %s." % fresult)
        return fresult

def test():
    key_exact = KeyExtract()
    key_exact.open()
    result = key_exact.get_keywords("""
去年开始， 打开百度李毅吧， 满屏的帖子大多含有“屌丝”二字，一般网友不仅不懂这词什么意思，更难理解这个词为什么会这么火。然而从下半年开始，“屌丝”已经覆盖网络各个角落，人人争说屌丝，人人争当屌丝。
    """)
    print result
    key_exact.close()

if __name__ == '__main__':
    test()
