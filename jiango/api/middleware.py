# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2017/4/23
"""


def get_token(request):
    return request.META.get("API_ACCESS_TOKEN", None)


class ApiAccessTokenMiddleware(object):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        print getattr(callback, 'use_access_token', False)
