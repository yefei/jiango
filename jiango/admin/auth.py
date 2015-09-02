# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
import hashlib
from uuid import uuid4
from functools import wraps
from django.utils.http import urlquote
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
from .models import User


COOKIE_NAME = 'jiango_admin_auth'
AUTHENTICATE_NEXT_FIELD = 'next'
REQUEST_ADMIN_FIELD = 'admin'


def auth_token_password(user):
    return hashlib.md5(':'.join((user.login_token, user.password_digest, settings.SECRET_KEY))).hexdigest()


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
    user.login_at = timezone.now()
    user.login_token = hashlib.md5(str(uuid4())).hexdigest()
    user.login_fails = 0
    User.objects.filter(pk=user.pk).update(login_at=user.login_at,
                                           login_token=user.login_token,
                                           login_fails=user.login_fails)


def set_logout(user):
    user.login_token = None
    User.objects.filter(pk=user.pk).update(login_token=None)


def set_login_cookie(response, user):
    token = str(user.login_token) + auth_token_password(user)
    response.set_cookie(COOKIE_NAME, token)


def set_logout_cookie(response):
    response.delete_cookie(COOKIE_NAME)


def get_admin_user(request):
    if hasattr(request, REQUEST_ADMIN_FIELD):
        return getattr(request, REQUEST_ADMIN_FIELD)
    user = get_user_from_auth_token(request.COOKIES.get(COOKIE_NAME))
    setattr(request, REQUEST_ADMIN_FIELD, user)
    return user


def login_redirect(request):
    path = urlquote(request.get_full_path())
    tup = reverse('admin:login'), AUTHENTICATE_NEXT_FIELD, path
    return HttpResponseRedirect('%s?%s=%s' % tup)


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if get_admin_user(request):
            return view_func(request, *args, **kwargs)
        return login_redirect(request)
    return wrapper


def logout_redirect(request):
    return HttpResponseRedirect(reverse('admin:index'))


def logout_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not get_admin_user(request):
            return view_func(request, *args, **kwargs)
        return logout_redirect(request)
    return wrapper
