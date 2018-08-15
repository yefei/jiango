# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/7/27 Feiye
Version: $Id:$
"""
from urllib import quote
from django.utils.encoding import smart_str


def get_remote_ip(request):
    return request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')) if request else None


def urlencode(items, encoding='utf-8'):
    return '&'.join(('%s=%s' % (
        quote(smart_str(k, encoding)), quote(smart_str(v, encoding))) for k, v in items.items()))
