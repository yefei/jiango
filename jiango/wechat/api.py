# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2019/3/24
"""
from functools import wraps
from jiango.api.helpers import APIResult
from jiango.api.errorcodes import WECHAT_AUTH_REQUIRED
from .auth import get_request_auth, get_authorization_redirect_url


def assert_get_wechat_auth(request):
    auth = get_request_auth(request)
    if not auth:
        raise APIResult(*WECHAT_AUTH_REQUIRED, redirect_url=get_authorization_redirect_url(request))
    return auth


def api_wechat_auth_required(api_func):
    @wraps(api_func)
    def wrapper(request, *args, **kwargs):
        assert_get_wechat_auth(request)
        return api_func(request, *args, **kwargs)
    return wrapper
