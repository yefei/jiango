# -*- coding: utf-8 -*-
# Created on 2015-12-2
# @author: Yefei
from django.forms import TextInput
from jiango.utils.humanize import humanize_second


class SecondInput(TextInput):
    def _format_value(self, value):
        if isinstance(value, (int, long)):
            return humanize_second(value)
        return value
