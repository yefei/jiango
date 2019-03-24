# -*- coding: utf-8 -*-
# Created on 2016-12-23
# @author: Fei Ye <316606233@qq.com>
from time import time
from functools import wraps
from base64 import urlsafe_b64encode, urlsafe_b64decode
from django.utils.http import cookie_date
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from jiango.crypto import crypto_data
from .settings import AUTH_COOKIE_KEY, AUTH_COOKIE_DOMAIN, AUTH_EXPIRES, AUTH_HEADER_KEY
from .models import Auth


AUTH_REDIRECT_NEXT_COOKIE_KEY = 'jiango_wechat_next'
AUTH_REQUEST_FIELD = '_jiango_wechat_auth'


def get_authorization_redirect_url(request=None):
    url = reverse('jiango-wechat-auth-redirect')
    if request:
        return request.build_absolute_uri(url)
    return url


def authorization_redirect(request):
    response = HttpResponseRedirect(get_authorization_redirect_url(request))
    response.set_cookie(AUTH_REDIRECT_NEXT_COOKIE_KEY, request.build_absolute_uri())
    return response


def get_auth_by_token(token):
    try:
        data = urlsafe_b64decode(token)
    except TypeError:
        return
    data = crypto_data.decrypt(data)
    if data is False:
        return
    try:
        return Auth.objects.get(pk=data)
    except Auth.DoesNotExist:
        pass


def get_request_auth_token(request):
    return request.COOKIES.get(AUTH_COOKIE_KEY, request.META.get(AUTH_HEADER_KEY))


def get_request_auth(request):
    if hasattr(request, AUTH_REQUEST_FIELD):
        return getattr(request, AUTH_REQUEST_FIELD)
    token = get_request_auth_token(request)
    if token:
        auth = get_auth_by_token(token)
        setattr(request, AUTH_REQUEST_FIELD, auth)
        return auth


# 生成一个认证 token, auth_id 为 Auth模型的id，expires 为有效时间（秒）
def make_auth_token(auth_id, expires=AUTH_EXPIRES):
    return urlsafe_b64encode(crypto_data.encrypt(str(auth_id), expires))


def set_auth_cookie(response, auth_token, expires=AUTH_EXPIRES, domain=AUTH_COOKIE_DOMAIN):
    expire_date = cookie_date(int(time() + expires)) if expires > 0 else None
    response.set_cookie(AUTH_COOKIE_KEY, auth_token, expires=expire_date, domain=domain)


def clear_auth_cookie(response, domain=AUTH_COOKIE_DOMAIN):
    response.delete_cookie(AUTH_COOKIE_KEY, domain=domain)


def wechat_auth_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if get_request_auth(request):
            return view_func(request, *args, **kwargs)
        return authorization_redirect(request)
    return wrapper
