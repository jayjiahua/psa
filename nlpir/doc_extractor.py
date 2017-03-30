# coding=utf-8

from __future__ import unicode_literals
from ctypes import (c_bool, c_char, c_char_p, c_double, c_int, c_uint,
                    c_ulong, c_void_p, cdll, POINTER, Structure)

from base import BaseNlpirSDK

import logging
import os
import sys

logger = logging.getLogger('nlpir.DocExtractor')


LIB_NAME = 'DocExtractor'
SHORT_NAME = 'DE'

class DocExtractor(BaseNlpirSDK):

    def __init__(self):
        BaseNlpirSDK.__init__(self, LIB_NAME, SHORT_NAME)

        # C函数定义
        # Get the exported NLPIR API functions.
        self.SentimentValue = self.get_func('DE_ComputeSentimentDoc', [c_char_p], c_int)

    def get_sentiment_value(self, s):
        s = self._decode(s)
        logger.debug("Get the sentiment value of the text: %s." % s)

        result = self.SentimentValue(self._encode(s))

        logger.debug("The sentiment value of the text is: %s." % result)

        return result

def test():
    doc_extractor = DocExtractor()
    doc_extractor.open()
    result = doc_extractor.get_sentiment_value("""
虽然今天遇到一点不顺心的事情，但总体上来说还是过得挺开心的。
    """)
    print result
    doc_extractor.close()

if __name__ == '__main__':
    test()
