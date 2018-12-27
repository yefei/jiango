# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/7/27 Feiye
Version: $Id:$
"""
from time import time
from functools import wraps
from django.utils.http import cookie_date, urlquote
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from jiango.api.exceptions import LoginRequired
from .services import get_request_user, get_request_login
from .settings import LOGIN_TOKEN_EXPIRED_SECONDS, LOGIN_COOKIE_NAME, LOGIN_VIEW_NAME, LOGIN_COOKIE_DOMAIN


def set_login_cookie(response, login, is_store=False, domain=LOGIN_COOKIE_DOMAIN):
    expires = cookie_date(int(time() + LOGIN_TOKEN_EXPIRED_SECONDS)) if is_store else None
    response.set_cookie(LOGIN_COOKIE_NAME, login.token, expires=expires, domain=domain)


def clear_login_cookie(response, domain=LOGIN_COOKIE_DOMAIN):
    response.delete_cookie(LOGIN_COOKIE_NAME, domain=domain)


def login_redirect(request):
    path = urlquote(request.get_full_path())
    return HttpResponseRedirect('%s?%s=%s' % (reverse(LOGIN_VIEW_NAME), 'ref', path))


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if get_request_login(request):
            return view_func(request, *args, **kwargs)
        return login_redirect(request)
    return wrapper


def assert_login_required(request):
    if not get_request_login(request):
        raise LoginRequired()


def api_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        assert_login_required(request)
        return view_func(request, *args, **kwargs)
    return wrapper


def user_inject(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = get_request_user(request)
        return view_func(request, user=user, *args, **kwargs)
    return wrapper
