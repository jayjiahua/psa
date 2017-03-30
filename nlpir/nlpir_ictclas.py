# coding=utf-8

from __future__ import unicode_literals
from ctypes import (c_bool, c_char, c_char_p, c_double, c_int, c_uint,
                    c_ulong, c_void_p, cdll, POINTER, Structure)

from base import BaseNlpirSDK

import logging
import os
import sys

logger = logging.getLogger('nlpir.NLPIR')


LIB_NAME = 'NLPIR'
SHORT_NAME = 'NLPIR'


POS_MAP = {
    'n': ('名词', 'noun', {
        'nr': ('人名', 'personal name', {
            'nr1': ('汉语姓氏', 'Chinese surname'),
            'nr2': ('汉语名字', 'Chinese given name'),
            'nrj': ('日语人名', 'Japanese personal name'),
            'nrf': ('音译人名', 'transcribed personal name')
        }),
        'ns': ('地名', 'toponym', {
            'nsf': ('音译地名', 'transcribed toponym'),
        }),
        'nt': ('机构团体名', 'organization/group name'),
        'nz': ('其它专名', 'other proper noun'),
        'nl': ('名词性惯用语', 'noun phrase'),
        'ng': ('名词性语素', 'noun morpheme'),
    }),
    't': ('时间词', 'time word', {
        'tg': ('时间词性语素', 'time morpheme'),
    }),
    's': ('处所词', 'locative word'),
    'f': ('方位词', 'noun of locality'),
    'v': ('动词', 'verb', {
        'vd': ('副动词', 'auxiliary verb'),
        'vn': ('名动词', 'noun-verb'),
        'vshi': ('动词"是"', 'verb 是'),
        'vyou': ('动词"有"', 'verb 有'),
        'vf': ('趋向动词', 'directional verb'),
        'vx': ('行事动词', 'performative verb'),
        'vi': ('不及物动词', 'intransitive verb'),
        'vl': ('动词性惯用语', 'verb phrase'),
        'vg': ('动词性语素', 'verb morpheme'),
    }),
    'a': ('形容词', 'adjective', {
        'ad': ('副形词', 'auxiliary adjective'),
        'an': ('名形词', 'noun-adjective'),
        'ag': ('形容词性语素', 'adjective morpheme'),
        'al': ('形容词性惯用语', 'adjective phrase'),
    }),
    'b': ('区别词', 'distinguishing word', {
        'bl': ('区别词性惯用语', 'distinguishing phrase'),
    }),
    'z': ('状态词', 'status word'),
    'r': ('代词', 'pronoun', {
        'rr': ('人称代词', 'personal pronoun'),
        'rz': ('指示代词', 'demonstrative pronoun', {
            'rzt': ('时间指示代词', 'temporal demonstrative pronoun'),
            'rzs': ('处所指示代词', 'locative demonstrative pronoun'),
            'rzv': ('谓词性指示代词', 'predicate demonstrative pronoun'),
        }),
        'ry': ('疑问代词', 'interrogative pronoun', {
            'ryt': ('时间疑问代词', 'temporal interrogative pronoun'),
            'rys': ('处所疑问代词', 'locative interrogative pronoun'),
            'ryv': ('谓词性疑问代词', 'predicate interrogative pronoun'),
        }),
        'rg': ('代词性语素', 'pronoun morpheme'),
    }),
    'm': ('数词', 'numeral', {
        'mq': ('数量词', 'numeral-plus-classifier compound'),
    }),
    'q': ('量词', 'classifier', {
        'qv': ('动量词', 'verbal classifier'),
        'qt': ('时量词', 'temporal classifier'),
    }),
    'd': ('副词', 'adverb'),
    'p': ('介词', 'preposition', {
        'pba': ('介词“把”', 'preposition 把'),
        'pbei': ('介词“被”', 'preposition 被'),
    }),
    'c': ('连词', 'conjunction', {
        'cc': ('并列连词', 'coordinating conjunction'),
    }),
    'u': ('助词', 'particle', {
        'uzhe': ('着', 'particle 着'),
        'ule': ('了／喽', 'particle 了/喽'),
        'uguo': ('过', 'particle 过'),
        'ude1': ('的／底', 'particle 的/底'),
        'ude2': ('地', 'particle 地'),
        'ude3': ('得', 'particle 得'),
        'usuo': ('所', 'particle 所'),
        'udeng': ('等／等等／云云', 'particle 等/等等/云云'),
        'uyy': ('一样／一般／似的／般', 'particle 一样/一般/似的/般'),
        'udh': ('的话', 'particle 的话'),
        'uls': ('来讲／来说／而言／说来', 'particle 来讲/来说/而言/说来'),
        'uzhi': ('之', 'particle 之'),
        'ulian': ('连', 'particle 连'),
    }),
    'e': ('叹词', 'interjection'),
    'y': ('语气词', 'modal particle'),
    'o': ('拟声词', 'onomatopoeia'),
    'h': ('前缀', 'prefix'),
    'k': ('后缀', 'suffix'),
    'x': ('字符串', 'string', {
        'xe': ('Email字符串', 'email address'),
        'xs': ('微博会话分隔符', 'hashtag'),
        'xm': ('表情符合', 'emoticon'),
        'xu': ('网址URL', 'URL'),
        'xx': ('非语素字', 'non-morpheme character'),
    }),
    'w': ('标点符号', 'punctuation mark', {
        'wkz': ('左括号', 'left parenthesis/bracket'),
        'wky': ('右括号', 'right parenthesis/bracket'),
        'wyz': ('左引号', 'left quotation mark'),
        'wyy': ('右引号', 'right quotation mark'),
        'wj': ('句号', 'period'),
        'ww': ('问号', 'question mark'),
        'wt': ('叹号', 'exclamation mark'),
        'wd': ('逗号', 'comma'),
        'wf': ('分号', 'semicolon'),
        'wn': ('顿号', 'enumeration comma'),
        'wm': ('冒号', 'colon'),
        'ws': ('省略号', 'ellipsis'),
        'wp': ('破折号', 'dash'),
        'wb': ('百分号千分号', 'percent/per mille sign'),
        'wh': ('单位符号', 'unit of measure sign'),
    }),
}


def _get_pos_name(pos_code, names='parent', english=True, pos_map=POS_MAP):
    """Gets the part of speech name for *pos_code*."""
    pos_code = pos_code.lower()  # Issue #10
    if names not in ('parent', 'child', 'all'):
        raise ValueError("names must be one of 'parent', 'child', or "
                         "'all'; not '%s'" % names)
    logger.debug("Getting %s POS name for '%s' formatted as '%s'." %
                 ('English' if english else 'Chinese', pos_code, names))
    for i in range(1, len(pos_code) + 1):
        try:
            pos_key = pos_code[0:i]
            pos_entry = pos_map[pos_key]
            break
        except KeyError:
            if i == len(pos_code):
                logger.warning("part of speech not recognized: '%s'"
                               % pos_code)
                return None  # Issue #20
    pos = (pos_entry[1 if english else 0], )

    if names == 'parent':
        logger.debug("Part of speech name found: '%s'" % pos[0])
        return pos[0]
    if len(pos_entry) == 3 and pos_key != pos_code:
        sub_map = pos_entry[2]
        logger.debug("Found parent part of speech name '%s'. Descending to "
                     "look for child name for '%s'" % (pos_entry[1], pos_code))
        sub_pos = _get_pos_name(pos_code, names, english, sub_map)
        pos = pos + sub_pos if names == 'all' else (sub_pos, )
    name = pos if names == 'all' else pos[-1]
    logger.debug("Part of speech name found: '%s'" % repr(name)
                 if isinstance(name, tuple) else name)
    return name


def get_pos_name(code, name='parent', english=True):
    """Gets the part of speech name for *code*.

    :param str code: The part of speech code to lookup, e.g. ``'nsf'``.
    :param str name: Which part of speech name to include in the output. Must
        be one of ``'parent'``, ``'child'``, or ``'all'``. Defaults to
        ``'parent'``. ``'parent'`` indicates that only the most generic name
        should be used, e.g. ``'noun'`` for ``'nsf'``. ``'child'`` indicates
        that the most specific name should be used, e.g.
        ``'transcribed toponym'`` for ``'nsf'``. ``'all'`` indicates that all
        names should be used, e.g. ``('noun', 'toponym',
        'transcribed toponym')`` for ``'nsf'``.
    :param bool english: Whether to return an English or Chinese name.
    :returns: ``str`` (``unicode`` for Python 2) if *name* is ``'parent'`` or
        ``'child'``. ``tuple`` if *name* is ``'all'``.

    """
    return _get_pos_name(code, name, english)


class NLPIR(BaseNlpirSDK):

    def __init__(self):
        BaseNlpirSDK.__init__(self, LIB_NAME, SHORT_NAME)

        # C函数定义
        # Get the exported NLPIR API functions.
        self.ParagraphProcess = self.get_func('NLPIR_ParagraphProcess', [c_char_p, c_int], c_char_p)
        self.ImportUserDict = self.get_func('NLPIR_ImportUserDict', [c_char_p], c_uint)
        self.AddUserWord = self.get_func('NLPIR_AddUserWord', [c_char_p])
        self.SaveTheUsrDic = self.get_func('NLPIR_SaveTheUsrDic')
        self.DelUsrWord = self.get_func('NLPIR_DelUsrWord', [c_char_p])

        self.WordFreqStat = self.get_func('NLPIR_WordFreqStat', [c_char_p], c_char_p)

    def segment(self, s, pos_tagging=True, pos_names='parent', pos_english=True):
        """Segment Chinese text *s* using NLPIR.

        The segmented tokens are returned as a list. Each item of the list is a
        string if *pos_tagging* is `False`, e.g. ``['我们', '是', ...]``. If
        *pos_tagging* is `True`, then each item is a tuple (``(token, pos)``), e.g.
        ``[('我们', 'pronoun'), ('是', 'verb'), ...]``.

        If *pos_tagging* is `True` and a segmented word is not recognized by
        NLPIR's part of speech tagger, then the part of speech code/name will
        be returned as :data:`None` (e.g. a space returns as ``(' ', None)``).

        This uses the function :func:`~pynlpir.nlpir.ParagraphProcess` to segment
        *s*.

        :param s: The Chinese text to segment. *s* should be Unicode or a UTF-8
            encoded string.
        :param bool pos_tagging: Whether or not to include part of speech tagging
            (defaults to ``True``).
        :param pos_names: What type of part of speech names to return. This
            argument is only used if *pos_tagging* is ``True``. :data:`None`
            means only the original NLPIR part of speech code will be returned.
            Other than :data:`None`, *pos_names* may be one of ``'parent'``,
            ``'child'``, or ``'all'``. Defaults to ``'parent'``. ``'parent'``
            indicates that only the most generic name should be used, e.g.
            ``'noun'`` for ``'nsf'``. ``'child'`` indicates that the most specific
            name should be used, e.g. ``'transcribed toponym'`` for ``'nsf'``.
            ``'all'`` indicates that all names should be used, e.g.
            ``'noun:toponym:transcribed toponym'`` for ``'nsf'``.
        :type pos_names: ``str`` or :data:`None`
        :param bool pos_english: Whether to use English or Chinese for the part
            of speech names, e.g. ``'conjunction'`` or ``'连词'``. Defaults to
            ``True``. This is only used if *pos_names* is ``True``.

        """
        s = self._decode(s)
        s = s.strip()
        logger.debug("Segmenting text with%s POS tagging: %s." %
                     ('' if pos_tagging else 'out', s))
        result = self.ParagraphProcess(self._encode(s), pos_tagging)
        result = self._decode(result)
        logger.debug("Finished segmenting text: %s." % result)
        logger.debug("Formatting segmented text.")
        tokens = result.strip().replace('  ', ' ').split(' ')
        tokens = [' ' if t == '' else t for t in tokens]
        if pos_tagging:
            for i, t in enumerate(tokens):
                token = tuple(t.rsplit('/', 1))
                if len(token) == 1:
                    token = (token[0], None)
                if pos_names is not None and token[1] is not None:
                    pos_name = get_pos_name(token[1], pos_names, pos_english)
                    token = (token[0], pos_name)
                tokens[i] = token
        logger.debug("Formatted segmented text: %s." % tokens)
        return tokens


    def segment_and_count(self, s, pos_names='parent', pos_english=True):
        s = self._decode(s)
        s = s.strip()
        result = self.WordFreqStat(self._encode(s))
        result = self._decode(result)
        tokens = result.strip("#").split('#')
        ret = []
        for token in tokens:
            try:
                token = token.split("/")
                if pos_names is not None and token[1] is not None:
                    pos_name = get_pos_name(token[1], pos_names, pos_english)
                    ret.append((token[0], pos_name, int(token[2])))
            except:
                pass
        return ret

def test():
    nlpir = NLPIR()
    nlpir.open()
    print nlpir.segment_and_count("""
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
    nlpir.close()

if __name__ == '__main__':
    test()
