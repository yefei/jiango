# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/7/27 Feiye
Version: $Id:$
"""
from jiango.shortcuts import get_object_or_none
from .models import Login
from .settings import *


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


def get_request_login(request):
    u"""
    通过当前请求取得登录对象
    :param request: 当前请求
    :return: 如果用户已经登录则返回 Login 对象，否则返回 None
    """
    if hasattr(request, 'login') and request.login:
        return request.login
    token = request.COOKIES.get(LOGIN_COOKIE_NAME, request.META.get(LOGIN_HEADER_NAME))
    if not token and hasattr(request, 'param'):
        token = request.param.get(LOGIN_API_PARAM_NAME)
    if token:
        request.login = get_login_by_token(token)
        if request.login:
            request.login.do_request(request)
        return request.login


def get_request_user(request):
    u"""
    通过当前请求取得登录用户
    :param request: 当前请求
    :return: 如果用户已经登录则返回 User 对象，否则返回 None
    """
    if hasattr(request, 'user') and request.user:
        return request.user
    login = get_request_login(request)
    if login:
        request.user = request.login.user
        return request.user
