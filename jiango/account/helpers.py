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
        login = getattr(request, 'login', None)
        if login is None:
            return login_redirect(request)
        return view_func(request, *args, **kwargs)
    return wrapper
