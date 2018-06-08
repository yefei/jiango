# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/6/8 Feiye
Version: $Id:$
"""
from jiango.ui import Element


class Label(Element):
    TAG = 'span'

    DEFAULT = 'default'
    PRIMARY = 'primary'
    SUCCESS = 'success'
    INFO = 'info'
    WARNING = 'warning'
    DANGER = 'danger'

    def __init__(self, content, type=DEFAULT):
        Element.__init__(self, content)
        self.set_attr('class', 'label label-%s' % type)
