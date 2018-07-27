# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/7/27 Feiye
Version: $Id:$
"""


def get_remote_ip(request):
    return request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')) if request else None
