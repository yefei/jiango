# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/7/27 Feiye
Version: $Id:$
"""
from jiango.shortcuts import get_object_or_none
from .models import Login


def get_login_by_token(token):
    u"""
    通过 token 获取有效的 Login实例
    :param token: token
    :return: Login
    """
    if token and len(token) == 32:
        login = get_object_or_none(Login, token=token)
        if login and login.is_active:
            return login
