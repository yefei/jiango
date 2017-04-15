# -*- coding: utf-8 -*-
# Copyright 2010 Yefe<yefe@ichuzhou.cn>
import os


class ChineseToPinyin(object):
    def __init__(self):
        self.table = {}
        with open(os.path.join(os.path.dirname(__file__), 'pinyin.txt'), 'r') as fp:
            for line in fp.readlines():
                self.table[ord(line[:3].decode('utf-8'))] = line[3:].strip()
            fp.close()

    def convert(self, value):
        pinyin = []
        ascii = []
        # 字符检查
        for c in list(unicode(value.lower() + ' ')):  # 加个空格多一次循环 修正尾部字符丢失问题
            c_ord = ord(c)
            if (47 < c_ord < 58) or (96 < c_ord < 123):  # 48-57[0-9]   97-122[a-z]
                ascii.append(c)
                continue
            if ascii:
                pinyin.append(''.join(ascii))
                ascii = []
            py = self.table.get(c_ord)
            if py:
                pinyin.append(py)
        return pinyin


chinese_to_pinyin = ChineseToPinyin()


if __name__ == '__main__':
    import time
    t = u'Prep 你好    中 国！I Love China! 2010年8月 !@    #   $%^   &* ()_+   Append'
    s = time.time()
    print '-'.join(chinese_to_pinyin.convert(t))  # you convert
    s = time.time()
    for i in xrange(0, 10000):
        chinese_to_pinyin.convert(t)  # you convert
    print 'convert:', time.time() - s
