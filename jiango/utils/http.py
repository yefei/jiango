# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2017/10/19
Version: $Id$
"""
from django.utils.http import same_origin


def safe_origin(request, url, fail=None):
    if '//' in url:
        if same_origin(request.build_absolute_uri(), url):
            return url
        return fail
    else:
        return url
