# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/6/9 Feiye
Version: $Id:$
"""
from jiango.ui import Element


class MainUI(Element):
    TAG = 'section'

    def __init__(self):
        Element.__init__(self)
        self.set_attr('class', 'content')

    def add_table(self, table):
        r = Element(table, tag='div', attrs={'class': 'table-responsive'})
        self.append(r)
