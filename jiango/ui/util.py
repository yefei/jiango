# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/6/8 Feiye
Version: $Id:$
"""
from django.utils.html import conditional_escape


def flatatt(attrs):
    out = []
    for k, v in attrs.items():
        if v:
            out.append('%s="%s"' % (k, conditional_escape(v)))
        else:
            out.append(k)
    return ' '.join(out)
