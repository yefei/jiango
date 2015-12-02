# -*- coding: utf-8 -*-
# Created on 2015-12-2
# @author: Yefei
from django.forms import Field
from django.core.validators import EMPTY_VALUES
from jiango.utils.humanize import parse_humanize_second
from .widgets import SecondInput


class SecondField(Field):
    widget = SecondInput
    
    def __init__(self, label=None, help_text=None, *args, **kwargs):
        label = label or u'秒数'
        help_text = help_text or u'1d=1天,1h=1小时,1m=1分钟,1s=1秒s可以不加。例如10天20小时15分3秒: 10d20h15m3'
        super(SecondField, self).__init__(label=label, help_text=help_text, *args, **kwargs)
    
    def to_python(self, value):
        if value in EMPTY_VALUES:
            return ''
        return parse_humanize_second(value)
