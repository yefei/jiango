# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2019/3/24
"""
from jiango.settings import PrefixSetting


setting = PrefixSetting('WECHAT_')


# 必须配置项
APP_ID = setting.get_setting('APP_ID')
SECRET = setting.get_setting('SECRET')
TOKEN = setting.get_setting('TOKEN')

SCOPE = setting.get_setting('SCOPE', 'snsapi_base')

AUTH_EXPIRES = setting.get_setting('AUTH_EXPIRES', 60 * 60 * 24 * 365)
AUTH_COOKIE_KEY = setting.get_setting('AUTH_COOKIE_KEY', 'jiango_wechat_auth')
AUTH_COOKIE_DOMAIN = setting.get_setting('AUTH_COOKIE_DOMAIN')
AUTH_HEADER_KEY = setting.get_setting('AUTH_HEADER_KEY', 'HTTP_X_WECHAT_AUTH_TOKEN')

# 支付支持
MCH_ID = setting.get_setting('MCH_ID')
PAY_KEY = setting.get_setting('PAY_KEY')
CERT = setting.get_setting('CERT')
CERT_KEY = setting.get_setting('CERT_KEY')
