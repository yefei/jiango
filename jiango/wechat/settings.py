# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2019/3/24
"""
from jiango.settings import PrefixSetting


setting = PrefixSetting('WECHAT_')


# 必须配置项
APP_ID = setting.get_required_setting('APP_ID')
SECRET = setting.get_required_setting('SECRET')
TOKEN = setting.get_required_setting('TOKEN')

SCOPE = setting.get_setting('SCOPE', 'snsapi_base')

AUTH_EXPIRES = setting.get_setting('AUTH_EXPIRES', 60 * 60 * 24 * 365)
AUTH_COOKIE_KEY = setting.get_setting('AUTH_COOKIE_KEY', 'jiango_wechat_auth')
AUTH_COOKIE_DOMAIN = setting.get_setting('AUTH_COOKIE_DOMAIN')
AUTH_HEADER_KEY = setting.get_setting('AUTH_HEADER_KEY', 'HTTP_X_WECHAT_AUTH_TOKEN')

# 是否开启支付支持
PAY_SUPPORT = setting.get_setting('PAY_SUPPORT', False)
if PAY_SUPPORT:
    PAY_KEY = setting.get_required_setting('PAY_KEY')
    MCH_ID = setting.get_required_setting('MCH_ID')
else:
    PAY_KEY = None
    MCH_ID = None
