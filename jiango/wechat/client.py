# -*- coding: utf-8 -*-
# Created on 2016-12-23
# @author: Fei Ye <316606233@qq.com>
import hashlib
import requests
import urllib
import json
from time import time
from django.core.cache import cache
from django.utils.html import escape
from django.utils.crypto import get_random_string
from django.conf import settings
from jiango.utils.xml2dict import XML2Dict
from .settings import APP_ID, SECRET, TOKEN, PAY_KEY, MCH_ID, SCOPE


ACCESS_TOKEN_CACHE_KEY = 'jiango:wechat:access_token'
JSAPI_TICKET_CACHE_KEY = 'jiango:wechat:jsapi_ticket'


class WeChatError(RuntimeError):
    def __init__(self, code, msg):
        self.errcode = code
        self.errmsg = msg
        super(WeChatError, self).__init__('[%d] %s' % (code, msg))


# 请求微信接口
def request_get(url, **params):
    resp = requests.get(url, params)
    data = json.loads(resp.content)  # 不能用自带的 resp.json() 因为 微信接口返回的中文不是 unicode 转义符
    if data.get('errcode', 0) != 0:
        raise WeChatError(data.get('errcode'), data.get('errmsg'))
    return data


def get_access_token():
    access_token = cache.get(ACCESS_TOKEN_CACHE_KEY)
    if access_token:
        return access_token
    data = request_get(
        'https://api.weixin.qq.com/cgi-bin/token',
        grant_type='client_credential',
        appid=APP_ID,
        secret=SECRET,
    )
    access_token = data.get('access_token')
    if access_token:
        cache.set(ACCESS_TOKEN_CACHE_KEY, access_token, data.get('expires_in') - 60)
        return access_token
    raise RuntimeError('no access_token')


def check_signature(params):
    signature = params.get('signature')
    timestamp = params.get('timestamp', '')
    nonce = params.get('nonce', '')
    tmp = [TOKEN, timestamp, nonce]
    tmp.sort()
    tmp_signature = hashlib.sha1(''.join(tmp)).hexdigest()
    return tmp_signature == signature


def jsapi_signature(params):
    keys = params.keys()
    keys.sort()
    s = '&'.join(['%s=%s' % (k, params[k]) for k in keys if params[k]])
    return hashlib.sha1(s.encode('utf-8')).hexdigest()


########################################################################################################################


# 取得微信网页授权跳转地址
def get_authorize_url(redirect_uri, scope=SCOPE, state=''):
    return 'https://open.weixin.qq.com/connect/oauth2/authorize' \
           '?appid=%s&redirect_uri=%s&response_type=code&scope=%s&state=%s#wechat_redirect' % (
        APP_ID, urllib.quote_plus(redirect_uri), scope, urllib.quote_plus(state))


# 解析网页授权返回的 code，并返回结果
def get_authorization_data(code):
    return request_get(
        'https://api.weixin.qq.com/sns/oauth2/access_token',
        grant_type='authorization_code',
        appid=APP_ID,
        secret=SECRET,
        code=code,
    )


# 刷新access_token
def get_authorization_data_by_refresh_token(refresh_token):
    return request_get(
        'https://api.weixin.qq.com/sns/oauth2/refresh_token',
        grant_type='refresh_token',
        appid=APP_ID,
        refresh_token=refresh_token,
    )


# 拉取用户信息(需scope为 snsapi_userinfo)
def get_user_info(access_token, openid, lang=None):
    return request_get(
        'https://api.weixin.qq.com/sns/userinfo',
        access_token=access_token,
        openid=openid,
        lang=lang or 'zh_CN',
    )


########################################################################################################################


def get_jsapi_ticket():
    ticket = cache.get(JSAPI_TICKET_CACHE_KEY)
    if ticket:
        return ticket
    data = request_get(
        'https://api.weixin.qq.com/cgi-bin/ticket/getticket',
        type='jsapi',
        access_token=get_access_token(),
    )
    ticket = data['ticket']
    cache.set(JSAPI_TICKET_CACHE_KEY, ticket, data.get('expires_in') - 60)
    return ticket


def get_jsapi_config(url, apis=None):
    timestamp = int(time())
    noncestr = get_random_string()
    ticket = get_jsapi_ticket()
    params = {
        'noncestr': noncestr,
        'jsapi_ticket': ticket,
        'timestamp': timestamp,
        'url': url,
    }
    sign = jsapi_signature(params)
    return {
        'debug': settings.DEBUG,  # 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
        'appId': APP_ID,  # 公众号的唯一标识
        'timestamp': timestamp,  # 生成签名的时间戳
        'nonceStr': noncestr,
        'signature': sign,
        'jsApiList': apis or [],
    }


########################################################################################################################


class WeChatPayError(RuntimeError):
    pass


def pay_signature(params):
    keys = params.keys()
    keys.sort()
    s = '&'.join(['%s=%s' % (k, params[k]) for k in keys if params[k]])
    s += '&key=' + PAY_KEY
    return hashlib.md5(s.encode('utf-8')).hexdigest().upper()


def pay_xml(params):
    params['sign'] = pay_signature(params)
    return '<xml>%s</xml>' % ''.join(['<%s>%s</%s>' % (k, escape(v), k) for k, v in params.items()])


def pay_xml_parse(xml_data):
    x = XML2Dict().parse(xml_data)
    x = x['xml']
    if x['return_code'] != 'SUCCESS':
        raise WeChatPayError(x['return_msg'])
    return x


def pay_unifiedorder(body, out_trade_no, total_fee, ip, notify_url, openid):
    url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
    params = {
        'appid': APP_ID,
        'mch_id': MCH_ID,
        # 'device_info': 'H5',
        'nonce_str': get_random_string(),
        # 'sign_type': 'MD5',
        'body': body,  # 商品描述
        'out_trade_no': out_trade_no,
        'total_fee': total_fee,  # 价格(分)
        'spbill_create_ip': ip,  # 客户端IP
        'notify_url': notify_url,  # 通知URL
        'trade_type': 'JSAPI',
        'openid': openid,
    }
    data = pay_xml(params)
    res = requests.post(url, data.encode('utf-8'))
    x = pay_xml_parse(res.content)
    if x['result_code'] != 'SUCCESS':
        raise WeChatPayError('%s: %s' % (x['err_code'], x['err_code_des']))
    return x


def get_jsapi_pay_config(prepay_id):
    timestamp = int(time())
    noncestr = get_random_string()
    params = {
        'appId': APP_ID,
        'timeStamp': str(timestamp),
        'nonceStr': noncestr,
        'package': 'prepay_id=%s' % prepay_id,
        'signType': 'MD5',
    }
    params['paySign'] = pay_signature(params)
    return params


def pay_notify_parse(xml_data):
    data = pay_xml_parse(xml_data)
    # 效验签名
    if data.pop('sign') == pay_signature(data):
        return data
    raise WeChatPayError('check signature error')
