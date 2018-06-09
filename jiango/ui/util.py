# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/6/8 Feiye
Version: $Id:$
"""
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape, escape
from django.utils.safestring import SafeData, EscapeData


def flatatt(attrs):
    out = []
    for k, v in attrs.items():
        if v:
            out.append('%s="%s"' % (k, conditional_escape(v)))
        else:
            out.append(k)
    return ' '.join(out)


def render_value(value):
    if callable(value):
        value = value()
    if not isinstance(value, SafeData) or isinstance(value, EscapeData):
        return escape(value)
    return force_unicode(value)
