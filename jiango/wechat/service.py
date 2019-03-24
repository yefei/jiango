# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2019/3/24
"""
from django.utils import timezone
from jiango.shortcuts import get_object_or_none
from .models import Auth
from .client import get_user_info, get_authorization_data_by_refresh_token


class WeChatRefreshExpired(RuntimeError):
    pass


def get_auth_by_openid(openid):
    return get_object_or_none(Auth, openid=openid)


def create_auth(openid, access_token, refresh_token, access_expires=7200, scope=''):
    now = timezone.now()
    return Auth.objects.create(
        openid=openid,
        access_token=access_token,
        refresh_token=refresh_token,
        access_expired_at=now + timezone.timedelta(seconds=access_expires),
        refresh_expired_at=now + timezone.timedelta(days=30),
        scope=scope,
    )


def update_auth(auth, data):
    update = False
    now = timezone.now()
    if auth.access_token != data['access_token']:
        auth.access_token = data['access_token']
        auth.access_expired_at = now + timezone.timedelta(seconds=data['expires_in'])
        update = True
    if auth.refresh_token != data['refresh_token']:
        auth.refresh_token = data['refresh_token']
        auth.refresh_expired_at = now + timezone.timedelta(days=30)
        update = True
    if auth.scope != data['scope']:
        auth.scope = data['scope']
        update = True
    if update:
        auth.save()
    return update


def get_by_authorization_data(data):
    auth = get_auth_by_openid(data['openid'])
    if auth:
        update_auth(auth, data)
    else:
        auth = create_auth(
            data['openid'],
            data['access_token'],
            data['refresh_token'],
            data['expires_in'],
            data['scope'],
        )
    return auth


def check_access_expired(auth):
    if auth.is_access_expired:
        if auth.is_refresh_expired:
            raise WeChatRefreshExpired()
        data = get_authorization_data_by_refresh_token(auth.refresh_token)
        update_auth(auth, data)


def get_user_info_by_auth(auth, lang=None):
    if auth.scope != 'snsapi_userinfo':
        raise RuntimeError('scope required snsapi_userinfo')
    check_access_expired(auth)
    return get_user_info(auth.access_token, auth.openid, lang)
