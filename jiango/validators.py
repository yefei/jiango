# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2017/10/7
Version: $Id$
"""
from django.core.validators import ValidationError
from django.utils.encoding import force_unicode


class StringSizeValidator(object):
    def __init__(self, min_size=0, max_size=0):
        self.min_size = min_size
        self.max_size = max_size

    def __call__(self, value):
        size = 0
        for c in force_unicode(value):
            # 字长判定，非 ASCII 字符算 2个长度
            size += 2 if ord(c) > 255 else 1
        params = {'min_size': self.min_size, 'max_size': self.max_size, 'show_value': size}
        if size < self.min_size:
            raise ValidationError(
                u'字长不能少于 %(min_size)d (当前长度 %(show_value)d)' % params,
                code='min_size',
                params=params,
            )
        if size > self.max_size > 0:
            raise ValidationError(
                u'字长不能长于 %(max_size)d (当前长度 %(show_value)d)' % params,
                code='max_size',
                params=params,
            )
