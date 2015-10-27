# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
import hashlib
from time import time
from uuid import uuid4
from functools import wraps
from django.utils.http import urlquote
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from jiango.shortcuts import update_instance
from .models import User
from .config import COOKIE_NAME, AUTH_SLAT_TIMEOUT, REQUEST_ADMIN_FIELD, LOGIN_NEXT_FIELD, SECRET_KEY_DIGEST


def auth_token_password(user):
    return hashlib.md5(':'.join((user.login_token, user.password_digest, SECRET_KEY_DIGEST))).hexdigest()


def get_temp_salt_verify(salt, salt_time):
    return hashlib.md5(salt + str(salt_time) + SECRET_KEY_DIGEST).hexdigest()


# 生成一个临时效验密匙
def get_temp_salt():
    salt = hashlib.md5(str(uuid4())).hexdigest()
    salt_time = str(int(time()))
    return salt + get_temp_salt_verify(salt, salt_time) + salt_time


def verify_temp_salt(value):
    if value and len(value) == 74:
        salt, verify, salt_time = value[:32], value[32:64], value[64:]
        if not salt_time.isdigit():
            return
        # 效验是否伪造
        if get_temp_salt_verify(salt, salt_time) != verify:
            return
        if int(time()) > (int(salt_time) + AUTH_SLAT_TIMEOUT):
            return False
        return True


def get_user_from_auth_token(value):
    if not value or len(value) != 64:
        return
    try:
        user = User.objects.get(login_token=value[:32])
    except User.DoesNotExist:
        return
    if auth_token_password(user) == value[32:]:
        return user


def set_login(user):
    update_instance(user,
                    login_at=timezone.now(),
                    login_token=hashlib.md5(str(uuid4())).hexdigest(),
                    login_fails=0)


def set_logout(user):
    update_instance(user, login_token=None)


def set_login_cookie(response, user):
    token = str(user.login_token) + auth_token_password(user)
    response.set_cookie(COOKIE_NAME, token)


def set_logout_cookie(response):
    response.delete_cookie(COOKIE_NAME)


def get_request_user(request):
    if hasattr(request, REQUEST_ADMIN_FIELD):
        return getattr(request, REQUEST_ADMIN_FIELD)
    user = get_user_from_auth_token(request.COOKIES.get(COOKIE_NAME))
    user and user.update_request_at()
    setattr(request, REQUEST_ADMIN_FIELD, user)
    return user


def login_redirect(request):
    path = urlquote(request.get_full_path())
    tup = reverse('admin:-login'), LOGIN_NEXT_FIELD, path
    return HttpResponseRedirect('%s?%s=%s' % tup)


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if get_request_user(request):
            return view_func(request, *args, **kwargs)
        return login_redirect(request)
    return wrapper


def logout_redirect(request):
    return HttpResponseRedirect(reverse('admin:-index'))


def logout_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not get_request_user(request):
            return view_func(request, *args, **kwargs)
        return logout_redirect(request)
    return wrapper
