# -*- coding: utf-8 -*-
# Created on 2015-10-10
# @author: Yefei
import re

COLUMN_PATH_RE = re.compile(u'^[_\.\-\w\u4e00-\uE814]+$')
COLUMN_PATH_HELP = u'可以输入 a-z、0-9、横线、下划线、点、汉字，用 / 来分割目录'
