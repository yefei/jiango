# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2017/3/25
Version: $Id: middleware.py 470 2017-08-01 05:39:43Z feiye $
"""
from .settings import *
from .services import get_request_user
from .helpers import clear_login_cookie


class LoginMiddleware(object):
    def process_request(self, request):
        get_request_user(request)
        return None

    def process_response(self, request, response):
        login = getattr(request, 'login', None)
        # 清除无效的 login cookie
        if login is None and LOGIN_COOKIE_NAME in request.COOKIES:
            clear_login_cookie(response)
        return response
