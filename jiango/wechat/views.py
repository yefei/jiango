# -*- coding: utf-8 -*-
# Created on 2016-12-23
# @author: Fei Ye <316606233@qq.com>
import logging
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from .client import check_signature, get_authorization_data, WeChatError, get_authorize_url
from .auth import set_auth_cookie, make_auth_token, AUTH_REDIRECT_NEXT_COOKIE_KEY, \
    wechat_auth_required, get_request_auth
from .service import get_by_authorization_data, get_user_info_by_auth


logger = logging.getLogger(__package__)


def callback(request):
    if not check_signature(request.GET):
        return HttpResponse('error signature!')
    if request.GET.has_key('echostr'):
        return HttpResponse(request.GET.get('echostr'))
    return HttpResponse('')


def auth_redirect(request):
    redirect_uri = request.build_absolute_uri(reverse('jiango-wechat-auth-callback'))
    response = HttpResponseRedirect(get_authorize_url(redirect_uri))
    next = request.GET.get('next')
    if next:
        response.set_cookie(AUTH_REDIRECT_NEXT_COOKIE_KEY, next)
    return response


def auth_callback(request):
    code = request.GET.get('code')
    if code:
        try:
            data = get_authorization_data(code)
            auth = get_by_authorization_data(data)
            token = make_auth_token(auth.id)
            url = request.COOKIES.get(AUTH_REDIRECT_NEXT_COOKIE_KEY, '/')
            if '?' in url:
                url += '&'
            else:
                url += '?'
            url += 'auth_token=%s' % token
            response = HttpResponseRedirect(url)
            response.delete_cookie(AUTH_REDIRECT_NEXT_COOKIE_KEY)
            set_auth_cookie(response, url)
            return response
        except WeChatError as e:
            logger.warn('authorization_code error: %s', e)
    return HttpResponse('authorization_code error!')


@wechat_auth_required
def auth_test(request):
    auth = get_request_auth(request)
    response = HttpResponse(u'wechat auth: %s' % auth)
    if auth.scope == 'snsapi_userinfo':
        response.write('\nuser info: %s' % get_user_info_by_auth(auth))
    return response
